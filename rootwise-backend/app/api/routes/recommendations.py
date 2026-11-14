
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.recommendation import (
    RecommendationRequest,
)
from app.services.recommendation_service import (
    FieldNotFoundError,
    build_recommendation_context,
    run_m1_recommendation_engine,
)

router = APIRouter(
    prefix="/recommend",
    tags=["Recommendations"],
)


@router.post("/")
def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    try:
        context = build_recommendation_context(
            db,
            request.field_id,
        )

        result = run_m1_recommendation_engine(
            context=context,
            target_season=request.target_season,
            target_year=request.target_year,
        )

        return result

    except FieldNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    except NotImplementedError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )
