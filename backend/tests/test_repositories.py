import pytest
from sqlalchemy import create_all, create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import Pedido
from ..repositories.order_repository import OrderRepository

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_order(db):
    repo = OrderRepository(db)
    new_order = Pedido(numero_ticket="T-001", total=25.5, estado="PENDIENTE", origen="KIOSKO")
    created = repo.create(new_order)
    
    assert created.id is not None
    assert created.numero_ticket == "T-001"
    assert created.total == 25.5

def test_get_today_orders(db):
    repo = OrderRepository(db)
    o1 = Pedido(numero_ticket="T-001", total=10, estado="COMPLETADO", origen="KIOSKO")
    repo.create(o1)
    
    orders = repo.get_today_orders()
    assert len(orders) == 1
    assert orders[0].numero_ticket == "T-001"
