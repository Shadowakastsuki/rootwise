
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.region import Region
from app.schemas.region import (
    RegionCreate,
    RegionUpdate,
    RegionResponse,
)

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("/", response_model=list[RegionResponse])
def get_regions(db: Session = Depends(get_db)):
    return db.scalars(
        select(Region).order_by(Region.id)
    ).all()


@router.get("/{region_id}", response_model=RegionResponse)
def get_region(region_id: int, db: Session = Depends(get_db)):
    region = db.get(Region, region_id)

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    return region


@router.post(
    "/",
    response_model=RegionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_region(data: RegionCreate, db: Session = Depends(get_db)):
    region = Region(**data.model_dump())

    try:
        db.add(region)
        db.commit()
        db.refresh(region)
        return region
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Region code already exists or data violates a database constraint",
        )


@router.patch("/{region_id}", response_model=RegionResponse)
def update_region(
    region_id: int,
    data: RegionUpdate,
    db: Session = Depends(get_db),
):
    region = db.get(Region, region_id)

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(region, key, value)

    try:
        db.commit()
        db.refresh(region)
        return region
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Region update violates a database constraint",
        )


@router.delete("/{region_id}")
def delete_region(region_id: int, db: Session = Depends(get_db)):
    region = db.get(Region, region_id)

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    try:
        db.delete(region)
        db.commit()
        return {"message": "Region deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this region because fields reference it",
        )
