# 🍗 Carbones y Pollos TPV - Enterprise Blueprint v2.0

Este documento detalla la arquitectura técnica y operativa del ecosistema profesional desarrollado para **Carbones y Pollos**. El sistema ha sido diseñado para ofrecer un rendimiento de grado empresarial, alta disponibilidad y capacidades de inteligencia artificial avanzada.

---

## 🏗️ Arquitectura del Sistema

El ecosistema opera bajo un modelo de **Computación Híbrida (Edge/Cloud)**:

1.  **Backend (FastAPI)**: Núcleo de alto rendimiento en Python. Gestiona la lógica de negocio, persistencia de datos (SQLite) y telemetría en tiempo real.
2.  **Frontend (Vanilla JS + Glassmorphism)**: Interfaces ultrarrápidas sin dependencias pesadas, optimizadas para pantallas táctiles y dispositivos móviles.
3.  **Capa de Resiliencia (Service Workers)**: Estrategia *Offline-First* que permite que el TPV y el Quiosko sigan operando incluso si la conexión a internet falla.
4.  **Inteligencia Artificial (Koal-AI)**: Integración nativa con Google Gemini para análisis de ventas, predicción de stock y asistencia administrativa.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Servidor** | FastAPI / Uvicorn | API REST de alto rendimiento y asíncrona. |
| **Base de Datos** | SQLAlchemy / SQLite | Persistencia local robusta con soporte para migraciones. |
| **IA** | Google Generative AI | Motor de razonamiento y análisis de datos. |
| **Telemetría** | Middleware Custom | Monitoreo de tiempos de respuesta y logs de seguridad. |
| **Frontend** | HTML5 / CSS3 / Tailwind | Diseño *Enterprise* con Inter font y Glassmorphism. |
| **PWA** | Service Workers (JS) | Caché inteligente y funcionamiento sin conexión. |

---

## 🔒 Seguridad y Telemetría

Se han implementado protocolos de blindaje profesional:

*   **SecurityHeadersMiddleware**: Inyección automática de cabeceras de seguridad (HSTS, CSP, XSS protection).
*   **Performance Telemetry**: Cada petición al servidor es auditada. Las peticiones que superan los 500ms generan alertas automáticas en los logs de administración.
*   **GZip Compression**: Reducción de hasta un 70% en el tamaño de transferencia de datos para máxima velocidad en redes 4G/5G.

---

## 📱 Componentes Clave

### 🛒 Quiosko Auto-Pedido
Interfaz minimalista diseñada para que el cliente final realice su pedido en segundos. 
*   **Iconografía Dinámica**: Los iconos se adaptan al nombre del producto.
*   **Checkout Local**: Procesamiento inmediato de pedidos con generación de número de ticket.

### 📊 Dashboard Administrativo
Centro de mando para la toma de decisiones basada en datos reales.
*   **Consola de Telemetría**: Visualización en vivo de la salud del sistema.
*   **Chat con Koal-AI**: Conversación natural con la base de datos del asador.

### ⚙️ Centro de Configuración
Gestión centralizada de variables críticas como la API Key de Gemini, la URL de sincronización Cloud y el ID del dispositivo.

---

## 🚀 Próximos Pasos (Roadmap)

1.  **Integración WAHA**: Automatización de envíos de reportes de cierre vía WhatsApp.
2.  **Cloud Sync Daemon**: Sincronización bidireccional automática con la base de datos central en la nube.
3.  **KDS (Kitchen Display System)**: Pantalla dedicada para cocina con tiempos de preparación en tiempo real.

> [!IMPORTANT]
> El sistema está listo para producción. Se recomienda mantener el archivo `.env` protegido y realizar backups periódicos del archivo `tpv.db`.
