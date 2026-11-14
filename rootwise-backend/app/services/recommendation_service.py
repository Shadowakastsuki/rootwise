from datetime import date

from rootwise_engine.api import recommend
from rootwise_engine.models import (
    RecommendRequest,
    FarmField,
    Climate,
)
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.field import Field
from app.models.crop import Crop
from app.models.farm_rotation import FarmRotation
from app.models.climate_feature import ClimateFeature


class FieldNotFoundError(Exception):
    pass


def build_recommendation_context(
    db: Session,
    field_id: int,
) -> dict:
    """
    Collects real database information needed by M1.
    This function does not calculate recommendations.
    """

    field = db.get(Field, field_id)

    if field is None:
        raise FieldNotFoundError("Field not found")

    region = field.region

    # Active crops available in the ROOTWISE crop catalogue
    crops = db.scalars(
        select(Crop)
        .where(Crop.is_active.is_(True))
        .order_by(Crop.name)
    ).all()

    # Previous crop rotations for this field
    rotations = db.scalars(
        select(FarmRotation)
        .where(FarmRotation.field_id == field_id)
        .order_by(FarmRotation.season_year.desc())
    ).all()

    # Recent climate observations for this field or its region
    climate_query = select(ClimateFeature).where(
        or_(
            ClimateFeature.field_id == field_id,
            ClimateFeature.region_id == field.region_id,
        )
    ).order_by(ClimateFeature.feature_date.desc()).limit(12)

    climate_records = db.scalars(climate_query).all()

    return {
        "field": {
            "id": field.id,
            "name": field.name,
            "region_id": field.region_id,
            "area_hectares": field.area_hectares,
            "soil_type": field.soil_type,
            "soil_ph": field.soil_ph,
            "irrigation_type": field.irrigation_type,
            "boundary_geojson": field.boundary_geojson,
            "region": {
                "name": region.name,
                "district": region.district,
                "state": region.state,
                "country": region.country,
            } if region else None,
        },
        "crop_catalog": [
            {
                "id": crop.id,
                "slug": crop.slug,
                "name": crop.name,
                "season": crop.season,
                "duration_days": crop.duration_days,
                "water_requirement": crop.water_requirement,
                "water_requirement_mm": crop.water_requirement_mm,
                "soil_preferences": crop.soil_preferences,
                "nutrient_needs": crop.nutrient_needs,
            }
            for crop in crops
        ],
        "rotation_history": [
            {
                "crop_id": rotation.crop_id,
                "crop_slug": rotation.crop.slug if rotation.crop else None,
                "crop_name": rotation.crop.name if rotation.crop else None,
                "season_year": rotation.season_year,
                "planting_date": (
                    rotation.planting_date.isoformat()
                    if rotation.planting_date else None
                ),
                "harvest_date": (
                    rotation.harvest_date.isoformat()
                    if rotation.harvest_date else None
                ),
                "yield_tonnes": rotation.yield_tonnes,
                "status": rotation.status,
            }
            for rotation in rotations
        ],
        "climate_observations": [
            {
                "source": item.source,
                "date": item.feature_date.isoformat(),
                "rainfall_mm": item.rainfall_mm,
                "temperature_min_c": item.temperature_min_c,
                "temperature_max_c": item.temperature_max_c,
                "humidity_pct": item.humidity_pct,
                "soil_moisture_pct": item.soil_moisture_pct,
                "ndvi": item.ndvi,
                "evapotranspiration_mm": item.evapotranspiration_mm,
                "data_quality": item.data_quality,
            }
            for item in climate_records
        ],
    }



def run_m1_recommendation_engine(
    context: dict,
    target_season: str,
    target_year: int,
) -> dict:
    """
    Adapt M3's database context to M1's recommendation contract.

    Missing environmental inputs remain unknown until M2
    provides verified data.
    """

    field_data = context["field"]
    region_data = field_data.get("region") or {}

    # Map only known field information.
    irrigation = (field_data.get("irrigation_type") or "").lower()

    if irrigation in ("rainfed", "rain-fed"):
        water_access = "rainfed"
    elif irrigation in ("irrigated", "drip", "sprinkler", "canal"):
        water_access = "irrigated"
    else:
        water_access = "unknown"

    # The M3 context currently contains no verified field
    # coordinates. M1's location defaults are Devanahalli.
    # Do not present these defaults as measured field coordinates.
    farm_field = FarmField(
        region_id=str(field_data["region_id"]),
        soil_type=field_data.get("soil_type"),
        water_access=water_access,
    )

    # No reliable seasonal climate aggregate is supplied yet.
    # M2 will eventually provide rainfall, ETc and daily data.
    climate = Climate(
        data_kind="missing",
        notes=[
            "M2 environmental data pipeline not connected.",
            "Field-specific coordinates not supplied.",
            "Season and year supplied by M3 are not yet used "
            "to construct a seasonal climate dataset.",
        ],
    )

    request = RecommendRequest(
        field=farm_field,
        climate=climate,
        as_of=date.today(),
    )

    result = recommend(request)

    response = result.model_dump(mode="json")

    response["request_context"] = {
        "field_id": field_data["id"],
        "target_season": target_season,
        "target_year": target_year,
        "region": region_data,
        "environmental_data_status": "pending_m2",
        "field_coordinates_status": "not_supplied",
    }

    return response
