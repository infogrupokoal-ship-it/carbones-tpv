import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import get_db, Base
from backend.routers.dependencies import get_current_user
from backend.models import Usuario

# Base de datos en memoria para tests ultrarrápidos
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from unittest.mock import MagicMock

def mock_admin_user():
    """Devuelve un usuario ADMIN simulado para tests, sin JWT real."""
    user = MagicMock(spec=Usuario)
    user.id = "test-admin-id"
    user.username = "test_admin"
    user.full_name = "Test Admin"
    user.rol = "ADMIN"
    user.is_active = True
    user.tienda_id = "test-tienda"
    return user

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user():
        return mock_admin_user()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

