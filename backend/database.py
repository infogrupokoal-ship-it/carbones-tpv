import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ruta de la base de datos profesionalizada
# En Render usamos el disco persistente montado en /data
if os.path.exists("/data") or os.environ.get("RENDER"):
    DB_PATH = "/data/tpv_data.sqlite"
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "tpv_data.sqlite")

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para obtener la sesión de la base de datos de forma segura."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
