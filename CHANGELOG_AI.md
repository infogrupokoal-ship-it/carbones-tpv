# CHANGELOG_AI.md

## [2026-05-02] - Singularity V10.0 Finalization

### Added
- `backend/routers/stats.py`: Added `get_sales_metrics` and `get_inventory_status` helper functions for AI services.
- `backend/services/ai_bi_agent.py`: Integrated `BusinessAIAgent` with real-time stats and `CierreZ` logic.

### Fixed
- `backend/main.py`: Consolidated all router inclusions (inventory, commercial, analytics, logistics, etc.).
- `backend/routers/inventory.py`: Fixed `listar_categorias` alias and router registration.
- `backend/routers/logistics.py`: Fixed missing `func` import from `sqlalchemy`.
- `backend/services/robotics_sim.py`: Added synchronous wrapper for safe thread execution.
- `backend/routers/enterprise_api.py`: Fixed missing `random` import.
- `backend/routers/notifications.py`: Fixed URL prefix duplication (removed `/api` from sub-router).
- `static/kiosko.html`: Unified product fetch URL to `/api/productos/`.

### Optimized
- `static/portal.html`: Enhanced UI with high-fidelity "Quantum V10.0" aesthetics and expanded module grid.
- `static/js/enterprise_shell.js`: Improved telemetry polling and Carbonito AI context interaction.
