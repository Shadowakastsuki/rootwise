
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.simulation import (
    SimulationCreate,
    SimulationResponse,
)
from app.services.simulation_service import (
    FieldNotFoundError,
    ScenarioNotFoundError,
    create_simulation,
    get_simulation,
    get_field_simulations,
)

router = APIRouter(
    prefix="/simulate",
    tags=["Simulations"],
)


@router.post(
    "/",
    response_model=SimulationResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_simulation(
    data: SimulationCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_simulation(
            db=db,
            field_id=data.field_id,
            title=data.title,
            description=data.description,
            input_parameters=data.input_parameters,
        )
    except FieldNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )


@router.get(
    "/{scenario_id}",
    response_model=SimulationResponse,
)
def retrieve_simulation(
    scenario_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_simulation(db, scenario_id)
    except ScenarioNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Simulation not found",
        )


@router.get(
    "/",
    response_model=list[SimulationResponse],
)
def retrieve_field_simulations(
    field_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_field_simulations(db, field_id)
    except FieldNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )
