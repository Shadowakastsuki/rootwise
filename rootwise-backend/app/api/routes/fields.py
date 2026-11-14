
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.field import Field
from app.models.region import Region
from app.schemas.field import (
    FieldCreate,
    FieldUpdate,
    FieldResponse,
)

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.get("/", response_model=list[FieldResponse])
def get_fields(
    region_id: int | None = None,
    farmer_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(Field)

    if region_id is not None:
        query = query.where(Field.region_id == region_id)

    if farmer_id is not None:
        query = query.where(Field.farmer_id == farmer_id)

    return db.scalars(query.order_by(Field.id)).all()


@router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    field = db.get(Field, field_id)

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    return field


@router.post(
    "/",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_field(data: FieldCreate, db: Session = Depends(get_db)):
    if not db.get(Region, data.region_id):
        raise HTTPException(status_code=404, detail="Region not found")

    field = Field(**data.model_dump())

    try:
        db.add(field)
        db.commit()
        db.refresh(field)
        return field
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Field data violates a database constraint. Check the farmer and region IDs.",
        )


@router.patch("/{field_id}", response_model=FieldResponse)
def update_field(
    field_id: int,
    data: FieldUpdate,
    db: Session = Depends(get_db),
):
    field = db.get(Field, field_id)

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    updates = data.model_dump(exclude_unset=True)

    if "region_id" in updates and updates["region_id"] is not None:
        if not db.get(Region, updates["region_id"]):
            raise HTTPException(status_code=404, detail="Region not found")

    for key, value in updates.items():
        setattr(field, key, value)

    try:
        db.commit()
        db.refresh(field)
        return field
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Field update violates a database constraint",
        )


@router.delete("/{field_id}")
def delete_field(field_id: int, db: Session = Depends(get_db)):
    field = db.get(Field, field_id)

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    try:
        db.delete(field)
        db.commit()
        return {"message": "Field deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this field because related records prevent deletion",
        )
