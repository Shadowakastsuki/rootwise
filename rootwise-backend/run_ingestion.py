from app.db.database import SessionLocal
from app.services.data_ingestion_service import ingest_bengaluru_dataset

db = SessionLocal()

try:
    result = ingest_bengaluru_dataset(db)
    print("INGESTION RESULT:")
    print(result)
except Exception as e:
    db.rollback()
    print("INGESTION FAILED:", str(e))
finally:
    db.close()
