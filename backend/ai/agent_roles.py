# backend/ai/agent_roles.py
class AgentRoles:
    ARCHITECT = {"model": "gemini-2.5-flash", "temp": 0.2, "role": "Diseña arquitectura y detecta riesgos."}
    CODER = {"model": "gemini-2.5-flash", "temp": 0.4, "role": "Genera o modifica código seguro."}
    REVIEWER = {"model": "gemini-2.5-flash", "temp": 0.1, "role": "Audita código en busca de errores."}
    TESTER = {"model": "gemini-2.5-flash", "temp": 0.3, "role": "Genera y valida pruebas."}
    DEVOPS = {"model": "gemini-2.5-flash", "temp": 0.2, "role": "Revisa configuraciones, Docker y Render."}
    SECURITY = {"model": "gemini-2.5-flash", "temp": 0.0, "role": "Verifica secretos, CSRF, permisos."}
    BUSINESS = {"model": "gemini-2.5-flash", "temp": 0.4, "role": "Revisa impacto en negocio y flujos TPV/CRM."}
    DOCS = {"model": "gemini-2.5-flash", "temp": 0.5, "role": "Genera CHANGELOG y Markdown."}
    AUDITOR = {"model": "gemini-2.5-flash", "temp": 0.1, "role": "Compara promesa vs realidad."}
