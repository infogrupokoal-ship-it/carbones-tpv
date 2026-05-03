# CURRENT SPRINT: Ecosistema Autónomo de Impresión en Android (Queue & Intent Architecture)

## 1. VISIÓN GENERAL DEL SPRINT

El núcleo de este ciclo de desarrollo es desvincular el acto de generar un comprobante fiscal del acto de interactuar con hardware físico. Actualmente existe una fricción de concurrencia e interfaz gráfica en los dispositivos móviles Android de tienda. El objetivo es estructurar una cola de impresión 100% asíncrona gestionada por el servidor, que interactúe de forma imperceptible (Zero-Touch) a través de Intents con la aplicación RawBT.

## 2. REQUISITOS DE INGENIERÍA (EPICS & STORIES)

### Epic 1: Backend Print Queue Management (Motor de Cola)

- **Historia 1.1 - Persistencia de Trabajos (Job Persistence):**
  Añadir un modelo de base de datos `PrintJob` que registre identificadores únicos (`uuid`), fecha de creación, *payload* de texto crudo o base64, canal de origen (TPV, Kiosko, Caja), dispositivo de destino (identificador de tablet), y estado estricto (`PENDING`, `IN_FLIGHT`, `COMPLETED`, `FAILED`).
- **Historia 1.2 - API Endpoints RESTful:**
  Implementar `/api/print/queue` (POST) para registrar un trabajo nuevo.
  Implementar `/api/print/queue/poll` (GET) para dispositivos que pregunten por trabajos pendientes.
  Implementar `/api/print/queue/{id}/ack` (PATCH) para que el dispositivo notifique el resultado exitoso (o fallido con error log) devuelto por la API del servicio puente.

### Epic 2: Frontend RawBT Intent Broker (Capa Cliente)

- **Historia 2.1 - Inyección Asíncrona:**
  Reescribir el driver de cliente `print_service.js` para que consulte la cola sin bloquear el hilo principal (Main Thread).
- **Historia 2.2 - Dispatcher del Intent:**
  Crear la rutina que empaqueta el contenido recuperado de la cola y genera un URI seguro (`intent://...#Intent;scheme=rawbt;...`). Disparar este evento capturando las excepciones en caso de que RawBT no esté instalado (redirección suave de fallback).
- **Historia 2.3 - Poller & Acknowledgment Loop:**
  Una vez despachado el Intent, establecer un micro-servicio (Web Worker preferiblemente) que reporte el ACK al backend para marcar el comprobante como procesado.

### Epic 3: Monitoreo Visual e Identidad Corporativa

- **Historia 3.1 - Notificaciones de Estado Industriales:**
  Añadir componentes (Toasts o Banners fijos en el navbar del Dashboard/TPV) con codificación de colores estricta (`#facc15` para alertas, ámbar para colas, verde para éxitos) reflejando el volumen de tickets pendientes en la memoria de la TPV en tiempo real.

## 3. CRITERIOS DE ACEPTACIÓN

1. El backend levanta sin errores de importación y pasa las auditorías de esquema.
2. Al pulsar "Pagar e Imprimir" en una tablet, no aparece ningún cuadro de diálogo de Chrome/Firefox, sino que la pantalla vuelve automáticamente a la orden principal en menos de 250ms, mientras RawBT imprime físicamente.
3. El estado del comprobante cambia efectivamente de PENDING a COMPLETED en la base de datos tras la emisión.
4. Cualquier error de comunicación registra un volcado de pila crítico (stack trace) en `.ai_agents/memory/known_errors.md`.
