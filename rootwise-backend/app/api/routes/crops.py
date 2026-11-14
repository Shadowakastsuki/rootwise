
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.crop import Crop
from app.schemas.crop import (
    CropCreate,
    CropUpdate,
    CropResponse,
)

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("/", response_model=list[CropResponse])
def get_crops(
    is_active: bool | None = True,
    db: Session = Depends(get_db),
):
    query = select(Crop)

    if is_active is not None:
        query = query.where(Crop.is_active == is_active)

    return db.scalars(query.order_by(Crop.name)).all()


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.get(Crop, crop_id)

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    return crop


@router.post(
    "/",
    response_model=CropResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_crop(data: CropCreate, db: Session = Depends(get_db)):
    crop = Crop(**data.model_dump())

    try:
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Crop slug already exists or data violates a database constraint",
        )


@router.patch("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: int,
    data: CropUpdate,
    db: Session = Depends(get_db),
):
    crop = db.get(Crop, crop_id)

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(crop, key, value)

    try:
        db.commit()
        db.refresh(crop)
        return crop
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Crop update violates a database constraint",
        )


@router.delete("/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.get(Crop, crop_id)

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    try:
        db.delete(crop)
        db.commit()
        return {"message": "Crop deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this crop because rotation records reference it",
        )
