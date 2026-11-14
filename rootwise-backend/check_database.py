
from sqlalchemy import text
from app.db.database import SessionLocal

db = SessionLocal()

try:
    region_id = db.execute(
        text("""
            SELECT id FROM regions
            WHERE code = 'KA-BENGALURU-URBAN'
        """)
    ).scalar()

    if region_id is None:
        print("Bengaluru Urban region not found.")
    else:
        map_count = db.execute(
            text("SELECT COUNT(*) FROM map_cells WHERE region_id = :rid"),
            {"rid": region_id}
        ).scalar()

        climate_count = db.execute(
            text("""
                SELECT COUNT(*) FROM climate_features
                WHERE region_id = :rid
                AND feature_date = '2016-01-01'
            """),
            {"rid": region_id}
        ).scalar()

        sources = db.execute(
            text("""
                SELECT source, COUNT(*)
                FROM climate_features
                WHERE region_id = :rid
                AND feature_date = '2016-01-01'
                GROUP BY source
            """),
            {"rid": region_id}
        ).all()

        print("MAP CELLS:", map_count)
        print("CLIMATE RECORDS:", climate_count)
        print("SOURCES:", sources)

finally:
    db.close()
