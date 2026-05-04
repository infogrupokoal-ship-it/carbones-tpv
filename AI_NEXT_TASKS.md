# AI NEXT TASKS & PRIORITIES

Este documento rastrea la pila de tareas actualizadas para el proyecto Carbones y Pollos TPV. Toda IA que inicie una sesión debe consultar esto antes de actuar.

## 🔴 BLOCKER / ALTA PRIORIDAD (Resolver Primero)

- [ ] **Tests Unitarios Rotos:** `pytest` devuelve `ValueError`. Revisar `tests/test_orders.py` o los imports en la suite de pruebas. El sistema no puede avanzar a producción segura si no pasa CI.
- [ ] **Base de Datos Sin Semilla Correcta:** Validar si el script `scripts/seed_ultra.py` inserta correctamente el menú actualizado (Chivitos, Brascadas) y no duplica productos en ejecuciones sucesivas (Idempotencia).
- [ ] **Aislamiento de Entorno Local:** Asegurarse de que el script `watchdog_bridge.bat` no compite por los puertos de Windows o se corrompe con procesos huérfanos.

## 🟡 MEDIA PRIORIDAD (UX & Features TPV)

- [ ] **Optimización Táctil de Kiosko (`kiosko.html`):** Los botones del TPV deben ser grandes. El sistema debe poder filtrar categorías rápido (Pollos, Bebidas, Raciones, Bocadillos).
- [ ] **Conexión Real con Impresoras:** Probar `local_printer_bridge.py` conectando con la UROVO vía red local (ESC/POS socket test).
- [ ] **Cierre de Caja (Reporte Z):** Crear o mejorar la vista de "Caja" (`caja`) para generar un ticket Z con el desglose del turno.

## 🟢 BAJA PRIORIDAD (IA y WhatsApp)

- [ ] **Webhook WhatsApp:** Habilitar el módulo en `backend/main.py` para que lea los mensajes de WAHA (WhatsApp HTTP API) y responda usando Gemini (Agente de Toma de Pedidos).
- [ ] **KDS de Cocina:** Añadir efecto de "Timbre" (Pitido HTML5 Audio) cuando entra una comanda nueva en el KDS, y hacer que la fila parpadee.

## Instrucciones Operativas

1. Escoger UNA tarea de la lista.
2. Escribir el plan.
3. Modificar el código, hacer tests locales.
4. Si está OK, marcar como completada en este archivo (`[x]`).
5. Actualizar `CHANGELOG_AI.md`.
