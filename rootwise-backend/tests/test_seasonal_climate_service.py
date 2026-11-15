
import pytest

from app.services.seasonal_climate_service import (
    build_seasonal_climate,
)


def test_historical_data_not_used_as_seasonal_data():
    environmental = {
        "status": "matched",
        "observations": [
            {"date": "2016-01-01", "rainfall_mm": 0.0}
        ],
    }

    climate = build_seasonal_climate(environmental)

    assert climate.data_kind == "missing"
    assert climate.seasonal_effective_rainfall_mm is None


def test_valid_seasonal_inputs():
    climate = build_seasonal_climate(
        environmental_data={},
        seasonal_inputs={
            "source_id": "controlled_test",
            "source_url": "https://example.org/test",
            "data_kind": "modelled",
            "seasonal_effective_rainfall_mm": 500,
            "seasonal_irrigation_mm": 0,
            "seasonal_etc_by_crop_mm": {
                "cowpea": 400,
            },
        },
    )

    assert climate.data_kind == "modelled"
    assert climate.seasonal_effective_rainfall_mm == 500


def test_missing_inputs_rejected():
    with pytest.raises(ValueError):
        build_seasonal_climate(
            environmental_data={},
            seasonal_inputs={"data_kind": "modelled"},
        )
