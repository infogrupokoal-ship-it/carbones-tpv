from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Corrección para compatibilidad con Render (postgres:// -> postgresql://)
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url, 
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    pool_pre_ping=True,
    pool_size=10 if "sqlite" not in db_url else None,
    max_overflow=20 if "sqlite" not in db_url else None
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
