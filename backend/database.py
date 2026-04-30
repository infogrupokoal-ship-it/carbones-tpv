import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tpv_data.sqlite")

# Normalización para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine_args = {
    "pool_pre_ping": True,
}

if "sqlite" in DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    # Optimización para PostgreSQL en producción
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
