import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Dual-compatible: defaults to a dedicated normalized SQLite application database,
# or connects to PostgreSQL if DATABASE_URL is configured.
DEFAULT_DB_URL = "sqlite:///aiia_app.db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)

is_sqlite = DATABASE_URL.startswith("sqlite")

engine_args = {}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

# Enable Foreign Keys and WAL mode for SQLite
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
