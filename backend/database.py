import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ruta de la base de datos profesionalizada
# Priorizamos un disco persistente si existe, o usamos la carpeta 'instance'
if os.path.exists("/data"):
    DB_PATH = "/data/tpv_data.sqlite"
else:
    # Asegurar que el directorio instance existe (también se hace en main.py)
    INSTANCE_DIR = os.path.join(os.getcwd(), "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    DB_PATH = os.path.join(INSTANCE_DIR, "tpv_data.sqlite")

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
