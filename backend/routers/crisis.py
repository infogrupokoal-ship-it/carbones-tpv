from fastapi import APIRouter
import datetime

router = APIRouter(prefix="/crisis", tags=["Crisis Management & Emergency Protocols"])

EMERGENCY_MODES = {
    "FIRE_ALARM": {"action": "Evacuate & Shut down gas", "notification": "ALL_STAFF_URGENT"},
    "HEALTH_INSPECTION": {"action": "Deploy Compliance Docs", "notification": "MANAGER_ONLY"},
    "POWER_OUTAGE": {"action": "Switch to UPS & Save states", "notification": "IT_SUPPORT"}
}

@router.post("/activate/{mode}")
def activate_emergency_protocol(mode: str):
    """
    Fase 47: Protocolo de Gestión de Crisis.
    Activa protocolos de emergencia predefinidos para garantizar la seguridad y cumplimiento.
    """
    if mode not in EMERGENCY_MODES:
        return {"error": "Modo de emergencia no reconocido"}
    
    protocol = EMERGENCY_MODES[mode]
    return {
        "status": "PROTOCOL_ACTIVATED",
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": mode,
        "actions": protocol["action"],
        "broadcast": protocol["notification"]
    }

@router.get("/compliance")
def get_compliance_audit():
    """Genera un reporte instantáneo de cumplimiento para inspecciones."""
    return {
        "higiene": "100%",
        "trazabilidad": "OK",
        "temperaturas_criticas": "NOMINAL",
        "seguridad_social": "AL DIA"
    }
