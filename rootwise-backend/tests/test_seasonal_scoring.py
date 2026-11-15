
from rootwise_engine.api import recommend
from rootwise_engine.models import (
    RecommendRequest,
    FarmField,
    Climate,
)


def make_request(rainfall):
    return RecommendRequest(
        field=FarmField(
            region_id="2",
            lat=12.887313,
            lon=77.333232,
            soil_type="loamy",
            water_access="rainfed",
        ),
        climate=Climate(
            data_kind="modelled",
            source_id="controlled_test_scenario",
            source_url="https://example.org/test-scenario",
            seasonal_effective_rainfall_mm=rainfall,
            seasonal_irrigation_mm=0,
            seasonal_etc_by_crop_mm={
                "cowpea": 400,
                "green_gram": 400,
                "groundnut": 400,
            },
            notes=[
                "Synthetic climate inputs for testing only."
            ],
        ),
    )


def extract_water_scores(result):
    data = result.model_dump(mode="json")
    candidates = data["candidate_scores"]

    scores = {}

    if isinstance(candidates, dict):
        candidates = list(candidates.values())

    for crop in candidates:
        crop_id = crop.get("crop_id") or crop.get("id")

        criteria = crop.get("criteria") or crop.get("subscores")

        if crop_id is None or criteria is None:
            raise AssertionError(
                f"Unexpected candidate score structure: {list(crop.keys())}"
            )

        scores[crop_id] = criteria["water_use"]["value"]

    return scores


def test_seasonal_rainfall_changes_water_scores():
    dry = recommend(make_request(100))
    wet = recommend(make_request(500))

    assert len(dry.strategies) == 3
    assert len(wet.strategies) == 3

    dry_scores = extract_water_scores(dry)
    wet_scores = extract_water_scores(wet)

    print("\nDry scenario:", dry_scores)
    print("Wet scenario:", wet_scores)

    assert dry_scores, "No crop scores were found"
    assert dry_scores.keys() == wet_scores.keys()

    improved = [
        crop_id
        for crop_id in dry_scores
        if dry_scores[crop_id] is not None
        and wet_scores[crop_id] is not None
        and wet_scores[crop_id] > dry_scores[crop_id]
    ]

    assert improved, (
        "Increasing seasonal rainfall should improve "
        "at least one crop's water-use score"
    )

    for crop_id in improved:
        print(
            f"{crop_id}: "
            f"{dry_scores[crop_id]} -> {wet_scores[crop_id]}"
        )
