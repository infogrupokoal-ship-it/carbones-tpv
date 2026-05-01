# COMMANDS.md

- **Windows PowerShell:** watchdog_bridge.bat (arranque), VENDER_TPV.bat, setup_industrial_tasks.bat.
- **Entorno Virtual:** env\Scripts\activate
- **Instalar Dependencias:** pip install -r requirements.txt
- **Git:** git status, git add ., git commit -m "...", git push
- **Render Deploy:** Despliegue automático o vía Blueprint 
ender.yaml (Build: pip install -r requirements.txt, Start: gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app ...)
- **Docker:** Posible uso en Render, pero localmente parece ejecutarse nativo.
