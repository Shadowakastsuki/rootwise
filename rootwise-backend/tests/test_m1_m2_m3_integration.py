
from app.db.database import SessionLocal
from app.services.recommendation_service import (
    build_recommendation_context,
    run_m1_recommendation_engine,
)


def test_complete_m1_m2_m3_integration():
    db = SessionLocal()

    try:
        context = build_recommendation_context(db, 2)

        environmental = context["environmental_data"]

        assert environmental["status"] == "matched"
        assert environmental["map_cell"]["cell_code"] == (
            "29_525_3710000_2789000"
        )

        observations = environmental["observations"]

        assert len(observations) >= 1
        assert observations[0]["date"] == "2016-01-01"
        assert observations[0]["rainfall_mm"] == 0.0

        result = run_m1_recommendation_engine(
            context,
            "kharif",
            2026,
        )

        assert len(result["strategies"]) == 3

        request_context = result["request_context"]

        assert (
            request_context["environmental_data_status"]
            == "historical_observations_available"
        )

        assert request_context["field_coordinates_status"] == "supplied"

        print("\nM1 + M2 + M3 integration successful")

    finally:
        db.close()
