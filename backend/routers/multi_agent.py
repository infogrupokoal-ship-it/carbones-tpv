from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Pedido, LogOperativo, Usuario
from ..ai.gemini_provider import GeminiProvider
from ..ai.agent_roles import AgentRoles
from ..utils.logger import logger

# Importar las dependencias de seguridad del módulo de autenticación
from .dependencies import require_manager

router = APIRouter(prefix="/agents", tags=["Autonomous Agents"])

@router.post("/audit-day")
async def run_daily_audit(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_manager) # Proteger con rol MANAGER o ADMIN
):
    """
    Inicia una auditoría multi-agente del día actual.
    Extrae ventas, pedidos cancelados y registros operativos para detectar anomalías.
    """
    try:
        today = date.today()
        
        # 1. Recopilar datos comerciales (Pedidos)
        pedidos_hoy = db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()
        total_ventas = sum(p.total for p in pedidos_hoy if p.estado != "cancelado")
        pedidos_cancelados = [p for p in pedidos_hoy if p.estado == "cancelado"]
        
        # 2. Recopilar métricas de Tickets (Pedidos con número de ticket)
        tickets_hoy = [p for p in pedidos_hoy if p.numero_ticket]
        
        # 3. Recopilar logs de seguridad recientes
        logs_hoy = db.query(LogOperativo).filter(func.date(LogOperativo.fecha) == today).order_by(LogOperativo.fecha.desc()).limit(50).all()
        
        # Resumen estructurado
        contexto = f"""
        REPORTE DEL DÍA: {today.isoformat()}
        - Pedidos Totales: {len(pedidos_hoy)}
        - Ventas Brutas Estimadas: {total_ventas}€
        - Pedidos Cancelados: {len(pedidos_cancelados)}
        - Tickets Registrados: {len(tickets_hoy)}
        
        LOGS OPERATIVOS DESTACADOS:
        """
        for log in logs_hoy:
            if log.nivel in ["WARNING", "ERROR", "CRITICAL"]:
                contexto += f"\n[{log.fecha.strftime('%H:%M')}] {log.modulo} - {log.nivel}: {log.mensaje}"

        if len(pedidos_cancelados) > 0:
            contexto += "\n\nDETALLE DE PEDIDOS CANCELADOS:"
            for p in pedidos_cancelados:
                contexto += f"\n- Pedido #{p.id}: {p.total}€ (Método: {p.metodo_pago})"

        # Instanciar a los agentes con perfiles mejorados
        business_instruction = (
            "Eres un analista de negocios experto. "
            "Revisa las ventas y métricas del día de un restaurante de comida rápida. "
            "Responde SIEMPRE en formato JSON con la siguiente estructura: "
            "{\"score\": 1-10, \"summary\": \"string\", \"insights\": [\"insight1\", \"insight2\"]}"
        )
        business_agent = GeminiProvider(
            model_name=AgentRoles.BUSINESS["model"], 
            system_instruction=business_instruction, 
            response_mime_type="application/json"
        )

        auditor_instruction = (
            "Eres un auditor de seguridad implacable. "
            "Busca anomalías, fraudes o problemas operativos en los logs y cancelaciones. "
            "Responde SIEMPRE en formato JSON con la siguiente estructura: "
            "{\"risk_level\": \"LOW\" o \"MEDIUM\" o \"HIGH\", \"anomalies\": [\"string\"], \"recommendations\": [\"string\"]}"
        )
        auditor_agent = GeminiProvider(
            model_name=AgentRoles.AUDITOR["model"], 
            system_instruction=auditor_instruction, 
            response_mime_type="application/json"
        )
        
        # Peticiones en paralelo para mayor velocidad
        business_prompt = "Analiza el rendimiento comercial del día basándote en los datos."
        auditor_prompt = "Audita el contexto operativo buscando problemas o confirmando seguridad."
        
        import asyncio
        import json
        
        def clean_json(text):
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        
        business_report_json, auditor_report_json = await asyncio.gather(
            business_agent.ask_async(business_prompt, context=contexto, temp=AgentRoles.BUSINESS["temp"]),
            auditor_agent.ask_async(auditor_prompt, context=contexto, temp=AgentRoles.AUDITOR["temp"])
        )
        
        try:
            b_data = json.loads(clean_json(business_report_json))
        except Exception as e:
            logger.error(f"Error parseando JSON de Business: {e}. Raw: {business_report_json}")
            b_data = {"score": 0, "summary": "Error parseando JSON de Business.", "insights": []}
            
        try:
            a_data = json.loads(clean_json(auditor_report_json))
        except Exception as e:
            logger.error(f"Error parseando JSON de Auditor: {e}. Raw: {auditor_report_json}")
            a_data = {"risk_level": "UNKNOWN", "anomalies": ["Error parseando JSON de Auditor."], "recommendations": []}

        # Generar un Markdown enriquecido a partir de los JSON
        risk_emoji = "🔴" if a_data.get("risk_level") == "HIGH" else "🟡" if a_data.get("risk_level") == "MEDIUM" else "🟢"
        
        # Helper lists formatter
        b_insights = "\n".join([f"- {i}" for i in b_data.get('insights', [])]) or "- Sin insights destacables."
        a_anomalies = "\n".join([f"- {a}" for a in a_data.get('anomalies', [])]) or "- No se detectaron anomalías."
        a_recs = "\n".join([f"- {r}" for r in a_data.get('recommendations', [])]) or "- Sistema operando normalmente."

        final_markdown = f"""## 📈 Análisis Comercial (Agente Business)
**Puntuación del Día:** {b_data.get('score', '?')}/10
**Resumen:** {b_data.get('summary', 'N/A')}

**Insights Clave:**
{b_insights}

---

## 🕵️ Auditoría de Seguridad (Agente Auditor)
**Nivel de Riesgo:** {risk_emoji} {a_data.get('risk_level')}

**Anomalías Detectadas:**
{a_anomalies}

**Recomendaciones:**
{a_recs}
"""
        return {"status": "success", "report": final_markdown}
        
    except Exception as e:
        logger.error(f"Error en Auditoría Multi-Agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))
