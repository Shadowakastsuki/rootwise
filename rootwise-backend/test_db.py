
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load database settings from .env
load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("DATABASE_URL is missing in .env")
else:
    try:
        engine = create_engine(database_url)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            print("\nSUCCESS! PostgreSQL connected.")
            print("Database:", connection.execute(
                text("SELECT current_database()")
            ).scalar())
            print("Version:", result.scalar())

        engine.dispose()

    except Exception as error:
        print("\nDATABASE CONNECTION FAILED")
        print(error)
