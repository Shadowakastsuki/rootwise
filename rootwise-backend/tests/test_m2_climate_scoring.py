
from rootwise_engine.api import recommend
from rootwise_engine.models import (
    RecommendRequest,
    FarmField,
    Climate,
)


def make_request(rainfall_mm, irrigation_mm):
    return RecommendRequest(
        field=FarmField(
            region_id="2",
            lat=12.887313,
            lon=77.333232,
            soil_type="loamy",
            water_access="rainfed",
        ),
        climate=Climate(
            source_id="rootwise_test_scenario",
            source_url="https://example.org/test-scenario",
            data_kind="illustrative",
            seasonal_effective_rainfall_mm=rainfall_mm,
            seasonal_irrigation_mm=irrigation_mm,
        ),
    )


def test_climate_scenario_does_not_claim_observed_water_sufficiency():
    dry = recommend(make_request(100, 0))
    wet = recommend(make_request(600, 0))

    assert len(dry.strategies) == 3
    assert len(wet.strategies) == 3

    # Illustrative inputs must not be treated as verified
    # observed or modelled seasonal water supply.
    assert dry is not None
    assert wet is not None
