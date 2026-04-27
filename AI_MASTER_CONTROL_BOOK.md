# DOCUMENTO TÉCNICO MAESTRO: OPERACIONES Y TELEMETRÍA TPV
**Proyecto:** Carbones y Pollos - Infraestructura TPV
**Clasificación:** Confidencial / Uso exclusivo de Ingeniería e IA.
**Fecha de Auditoría y Sellado:** 27 de Abril de 2026.

---

## 1. RESUMEN EJECUTIVO
Este documento establece el marco operativo estandarizado para la infraestructura de Punto de Venta (TPV). El sistema ha sido migrado satisfactoriamente de una arquitectura dependiente a un modelo de **Edge Computing Autónomo** operando bajo Android (Termux). Este diseño garantiza tolerancia a fallos de red, persistencia de datos local (Offline-First) y capacidad de gestión remota asíncrona.

---

## 2. ARQUITECTURA DE SISTEMAS Y TOPOLOGÍA DE RED

### 2.1 Hardware y Entorno de Ejecución
*   **Dispositivo Core:** Hardware propietario Sunmi POS (Arquitectura ARM) con Impresora Térmica y Cajón Portamonedas (RJ11) integrados.
*   **Sistema Operativo Base:** Android OS (Restringido - Seguridad Kiosko).
*   **Capa de Virtualización (Userspace):** Termux Environment.
*   **Runtime:** Python 3.13 (Aislado mediante `venv`).

### 2.2 Stack de Software
*   **Backend API:** FastAPI ejecutándose sobre el servidor ASGI Uvicorn (Puerto `5001`).
*   **Bases de Datos:** SQLite (`tpv_data.sqlite`). Transacciones atómicas locales que previenen pérdida de datos en caídas de tensión.
*   **Microservicio de Hardware (Puente Híbrido):** `local_printer_bridge.py` (Puerto `8000`). Este módulo detecta la plataforma operativa. En Android, envía comandos binarios ESC/POS (incluyendo el código de apertura de cajón `\x1B\x70\x00\x19\xFA`) a través de paquetes HTTP nativos hacia el servidor WebSocket local de **RawBT** (Puerto `40213`), evadiendo así las restricciones de Android Intents para comandos crudos.

### 2.3 Matriz de Integración de Periféricos (Hardware Externo)
Se tiene constancia de hardware adicional acoplado a la TPV (ej. Impresoras de cocina LAN, Escáneres USB, Terminales de Pago, etc.), previamente gestionados por la app legacy `co.dish.posapp.dish`. El protocolo de asimilación para futuras IAs es el siguiente:
1.  **Impresoras de Red (LAN/WLAN):** Las impresoras de red (ej. Cocina) operan típicamente en el puerto TCP `9100`. Python puede establecer un socket TCP directo sin necesidad de drivers adicionales ni RawBT.
2.  **Periféricos USB (Lectores de Códigos/Básculas):** Android maneja lectores de códigos de barras como teclados físicos (HID). Las pulsaciones entran directamente al foco del navegador (PWA). No requieren drivers, pero el Frontend web debe escuchar eventos `onKeyDown`.
3.  **Datáfonos (PinPads):** Requieren integración vía API Web o comunicación serie sobre IP si la red local lo permite. La IA deberá sondear la subred local (`nmap -sn`) en la tienda para identificar las IPs asignadas a estos dispositivos.

---

## 3. PROTOCOLOS DE GOBERNANZA Y ACCESO REMOTO (R.A.P)

Ante la inminente reubicación del hardware a una nueva topología de red (Local Comercial), se ha implementado un protocolo de resiliencia de conexión.

### 3.1 Acceso Primario (LAN)
Aplicable únicamente cuando el nodo de control (PC) y la TPV coexisten en la misma subred.
*   **Protocolo:** SSH Puenteado a través del script local `ssh_cmd.py`.
*   **Puerto de Escucha Termux:** `8022`.

### 3.2 Acceso Secundario: Túnel Criptográfico Inverso (WAN)
Implementado para superar el problema de NAT estricto y DHCP dinámico en el local comercial.
*   **Ejecutable de Activación:** `/data/data/com.termux/files/home/remote_support.sh`
*   **Mecanismo:** El script inicializa un túnel reverso mediante el protocolo SSH hacia la pasarela global de Pinggy (`a.pinggy.io`).
*   **Procedimiento Operativo Estándar (SOP) para Operadores:**
    1. Abrir la terminal Termux en el dispositivo.
    2. Ejecutar comando de inyección: `./remote_support.sh`
    3. Recuperar el end-point TCP generado (Ej. `tcp://x.pinggy.link:PORT`).
    4. Proporcionar el end-point a la IA de gestión para establecer enlace shell global.

---

## 4. DAEMONIZACIÓN Y RECUPERACIÓN ANTE DESASTRES (D.R.P)

El ecosistema posee mecanismos de auto-sanación, pero su manipulación directa por IAs requiere adherencia estricta a los siguientes lineamientos:

### 4.1 Prevención de Bloqueos de Puertos (Error 98)
El entorno Termux gestiona los sockets TCP de forma restrictiva. Múltiples hilos o reinicios forzados (`reload=True`) causan el bloqueo del puerto `5001`.
*   **Comando de Purgado Obligatorio:** Previo a cualquier reinicio de servicios, la IA debe asegurar la terminación de procesos huérfanos:
    `killall python || true && killall bash || true`

### 4.2 Secuencia de Ignición Autónoma
El sistema está diseñado para arrancar en frío desde el script maestro.
*   **Vector de Arranque:** `/data/data/com.termux/files/home/.termux/boot/tpv_daemon.sh`
*   **Bloqueo de Suspensión:** Se invoca `termux-wake-lock` de forma predeterminada para evitar que el Doze Mode de Android suspenda el servidor web cuando la pantalla se apaga.

---

## 5. RESTRICCIONES DE SEGURIDAD (OS-LEVEL) Y AUDITORÍA DE ADWARE

Durante la fase de estabilización se detectaron paquetes de bloatware (`com.ss.android.ugc.tiktok.pro`, `cm.aptoide.pt`).
*   **Resolución de la IA:** Se ha emitido la señal de terminación (`pm uninstall`), resultando en una denegación de permisos (`SecurityException: PID does not have permission android.permission.DELETE_PACKAGES`).
*   **Directriz de Seguridad Operativa:** Es mandatorio que el operador humano realice el purgado de caché y datos del navegador Chrome manualmente desde los "Ajustes de Android". La arquitectura de seguridad del Kernel Android prohíbe explícitamente a los procesos de Termux la eliminación de aplicaciones de terceros sin privilegios de Root.
*   **Preservación de Activos:** La aplicación "Dish POS" (`co.dish.posapp.dish`) se mantiene en estado estático (no ejecutada, no eliminada) cumpliendo con la orden de preservación para contingencias logísticas.

---

## 6. DECLARACIÓN DE CERTIFICACIÓN DE PASE A PRODUCCIÓN

La infraestructura certifica el cumplimiento de los tres requerimientos fundamentales para la puesta en marcha ("Go-Live"):
1.  **Aislamiento Comercial (Kiosko):** Preparado vía PWA (Progressive Web App) en Chrome.
2.  **Autonomía de Datos:** Base de datos validada para operaciones sin red externa.
3.  **Persistencia Remota:** Script de soporte remoto (WAN) inyectado y funcional.
4.  **Panel de Control Remoto (Fase 8):** Creado `admin_mobile.html` protegido con PIN, que se comunica con el servidor en la nube para encolar comandos de hardware.
5.  **Cloud-Edge Bridge (Fase 8):** Implementado un hilo de *Long-Polling* en `local_printer_bridge.py` que consulta el endpoint Cloud.

---

## 7. AVISO CRÍTICO DE ARQUITECTURA PARA FUTURAS IAs (LA "PUERTA ONLINE")

**ATENCIÓN IA:** El sistema TPV ya NO depende de conexiones de red local (RJ45/LAN) directas para comunicarse con los periféricos (impresora y cajón portamonedas).

*   **Arquitectura Desacoplada:** El backend principal vive en **Render (Cloud)**.
*   **Puerta Online (Polling):** La máquina física de la tienda (tablet/PC) ejecuta `local_printer_bridge.py`. Este script es un demonio local que realiza peticiones HTTP (Long-Polling) constantemente al endpoint de Render (`/api/hardware/poll`).
*   **Gestión de Hardware:** Cuando la Nube en Render quiere imprimir un ticket o abrir el cajón, NO hace un PUSH (ya no hace falta Ngrok ni IP fija). En su lugar, Render guarda el comando (`HardwareCommand` en SQLite). El `local_printer_bridge.py` del restaurante "recoge" ese comando e interactúa con el hardware a través de `win32print` o `RawBT` dependiendo del SO local.
*   **Resiliencia Operativa:** Si el TPV físico se mueve al trabajo o a otra red, **el sistema de impresión remoto seguirá funcionando sin configuración de red adicional**, siempre que el dispositivo local tenga acceso a Internet y `local_printer_bridge.py` esté corriendo.

**FIN DEL REPORTE.**
