import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_ai_bi_insights_endpoint():
    """Valida que el nuevo motor de BI proactivo devuelva insights válidos."""
    response = client.get("/api/telemetry/insights")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "system_health" in data
    assert len(data["insights"]) > 0
    assert "neural_load" in data["system_health"]

def test_digital_twin_nodes():
    """Verifica la integridad de los datos del Gemelo Digital."""
    response = client.get("/api/telemetry/global-nodes")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert data["total_nodes"] == len(data["nodes"])
    # Verificar que el nodo crítico OVEN-MASTER esté presente
    oven = next((n for n in data["nodes"] if n["id"] == "OVEN-MASTER"), None)
    assert oven is not None
    assert oven["status"] == "ACTIVE"

def test_telemetry_logs_access():
    """Verifica que el endpoint de logs sea accesible (simulado)."""
    response = client.get("/api/telemetry/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    # En local/test puede que no haya logs reales, pero el endpoint debe responder
    assert isinstance(data["logs"], dict)
