
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.data_ingestion_service import (
    ingest_bengaluru_dataset,
)

router = APIRouter(
    prefix="",
    tags=["Data Ingestion"],
)


@router.post("/ingest/grid-data")
def ingest_grid_data(
    db: Session = Depends(get_db),
):
    """
    Import Bengaluru Urban satellite grid data
    into the ROOTWISE PostgreSQL database.
    """

    try:
        result = ingest_bengaluru_dataset(db)
        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database ingestion failed. Changes were rolled back.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected ingestion error. Changes were rolled back.",
        )
