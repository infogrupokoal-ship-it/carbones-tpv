# 🚀 PLAN ESTRATÉGICO Y MASTER ROADMAP: CARBONES Y POLLOS

**Proyecto:** Migración a Edge Computing y Autonomía de TPV
**Teléfono Sistema (Tienda):** Próximo a definir (Comidas para Llevar)
**Teléfono Admin (Reportes):** `+34 604 86 41 87`

Este documento contiene la hoja de ruta exhaustiva y profesional diseñada para llevar la TPV de un estado básico a un sistema de gestión empresarial inteligente, autónomo y completamente resiliente, dividido en Fases lógicas de ejecución.

---

## 🟢 FASE 1: GO-LIVE Y DESPLIEGUE AUTÓNOMO (DÍA 1 - MAÑANA)

**Objetivo:** Conseguir que la TPV funcione sin depender de un PC con Windows, que controle el hardware local y que sea "a prueba de cocineros" (tolerante a apagones y reinicios).

### 1.1. Arranque "A Prueba de Cocineros" (Acceso Directo)
El sistema está diseñado para que cualquier empleado pueda encender la TPV sin conocimientos técnicos tras un corte de luz.
* **Motor Interno (Termux Widget):**
  * Descargar la app **Termux:Widget** desde F-Droid.
  * Añadir el Widget a la pantalla de inicio seleccionando el script `tpv_daemon.sh`.
  * *Resultado:* Un botón gigante en el escritorio llamado "Arrancar TPV".
* **Pantalla de Ventas (Chrome PWA):**
  * Abrir Chrome en `http://127.0.0.1:5001`.
  * "Añadir a la pantalla de inicio".
  * *Resultado:* Icono de App Nativa.

### 1.2. Conexión de Hardware Local (Impresora y Caja)
* Instalar **RawBT** en la tablet.
* Configurar en modo "Impresora Interna (Sunmi)" y habilitar el servidor WebSocket/HTTP interno.
* *El backend de la TPV ya está parcheado para mandar los comandos binarios (`\x1B\x70...`) directamente a RawBT sin pasar por drivers de Windows.*

### 1.3. Puente Criptográfico de Emergencia (Admin)
* Ejecutar `./remote_support.sh` en Termux.
* Proveerá una URL (túnel inverso) para que la IA de gestión pueda entrar por SSH desde cualquier lugar y arreglar bloqueos si el sistema falla.

---

## 🟡 FASE 2: TELEMETRÍA Y CIERRE DE CAJA VÍA WHATSAPP (DÍA 2)

**Objetivo:** Automatizar el reporte financiero nocturno para que el dueño tenga el control total sin estar físicamente en la tienda.

### 2.1. Arquitectura del Motor WAHA (Comidas para Llevar -> Admin)
* Se levantará un motor WAHA ligero en el ecosistema (o se reutilizará el VPS de Grupo Koal).
* Se escaneará el código QR con el **teléfono móvil de la tienda (Comidas para llevar)**.
* Este teléfono actuará como "Emisor Oficial" de las notificaciones del sistema.

### 2.2. Script de Cierre Z (`reporte_z.py`)
* Se programará un *Cronjob* en Termux que se ejecutará todos los días a las **23:59**.
* Extraerá de la base de datos `tpv_data.sqlite` la suma total de cobros en tarjeta y efectivo.
* Enviará un payload JSON a la API de WhatsApp para que el móvil de la tienda envíe este mensaje al **604 86 41 87**:
  ```text
  🐔 *CIERRE Z - CARBONES Y POLLOS* 🐔
  📅 Fecha: 28/04/2026
  💰 Efectivo: 120.50 €
  💳 Tarjeta: 330.00 €
  📊 TOTAL CAJA: 450.50 €
  🍗 Pollos Vendidos: 32
  ```

---

## 🟠 FASE 3: MOTOR DE INVENTARIO Y MERMAS AUTOMÁTICAS (DÍA 3 - 4)

**Objetivo:** Llevar un control estricto de las existencias para evitar pérdidas y calcular la rentabilidad real de los insumos.

### 3.1. Esquema de Base de Datos (Módulo Inventario)
Se ordenará a la IA que inyecte la tabla `inventory` en `tpv_data.sqlite` con las siguientes categorías maestras:
* Pollos Crudos (Unidades)
* Pollos Asados (Unidades)
* Carbón (Sacos / Kg)
* Bebidas (Latas / Botellas)

### 3.2. Lógica de "Merma Automática" (Hooks de Venta)
* Se modificará el endpoint `/pay` (o equivalente) en `main.py`.
* **Regla de Negocio:** Por cada "1 Pollo Asado" vendido en la TPV, el sistema automáticamente:
  1. Resta 1 unidad de la columna "Pollos Asados" en inventario.
  2. Registra el movimiento en una tabla de auditoría (`stock_movements`).

### 3.3. Interfaz de Cocina / Reposición
* Se creará una vista `http://127.0.0.1:5001/inventario` (protegida con PIN simple).
* Los empleados podrán registrar "Entrada de Proveedor" (ej. +50 Pollos Crudos) o "Paso a Asador" (Resta 10 Crudos, Suma 10 Asados).

---

## 🔴 FASE 4: ALERTAS PREDICTIVAS Y PEDIDOS A PROVEEDORES (DÍA 5)

**Objetivo:** Evitar roturas de stock mediante IA y notificaciones proactivas.

### 4.1. Umbrales Críticos
* Se establecerán límites rojos (ej. "Menos de 10 pollos crudos", "Menos de 2 sacos de carbón").
* Si al hacer una venta se cruza ese umbral límite, el sistema disparará un **WhatsApp de Alerta Inmediata** al `604 86 41 87` avisando de la falta de stock.

### 4.2. Módulo de Proveedores (Básico)
* Tabla de proveedores frecuentes (Nombre, Teléfono, Insumo principal).
* Botón en la TPV: "Solicitar más Pollos", que formatea un mensaje predefinido para enviarlo al proveedor directamente vía WhatsApp.

---

## 🟣 FASE 5: DASHBOARD EJECUTIVO Y AUDITORÍA (DÍA 6 - 7)

**Objetivo:** Consolidar la información para toma de decisiones estratégicas.

### 5.1. Dashboard Web Remoto
* Integrar los datos de SQLite locales en un panel web ligero usando `Chart.js`.
* Gráficas de "Ventas por hora" (para identificar picos de calor en el asador).
* Gráficas de "Rentabilidad" (Coste del pollo crudo + carbón vs. Precio de venta).

### 5.2. Auto-Mantenimiento de la Base de Datos
* Rotación de logs automáticos.
* Compresión periódica de SQLite (`VACUUM`) para mantener la TPV rápida y evitar que la tablet se quede sin espacio con el paso de los años.
* Copia de seguridad automática semanal enviada por WhatsApp (el archivo `.sqlite` o un `.csv`) a tu teléfono personal como salvaguarda ante robo o rotura de la tablet.

---

## 🟣 FASE 6: IA OMNICANAL VÍA WHATSAPP (DÍA 8 - 9)

**Objetivo:** Eliminar la carga manual de toma de pedidos a domicilio y el reporte de inventario mediante inteligencia artificial generativa (Google Gemini).

### 6.1. Reporte de Cocineros (Entrada de Inventario)
* Los cocineros o responsables de turno pueden enviar un audio o texto por WhatsApp: *"He sacado 20 pollos, 15 de arroz y 5 codillos"*.
* La IA interpretará el lenguaje natural, identificará los productos en la base de datos y añadirá el stock automáticamente.
* La IA responderá confirmando: *"Entendido. Sumados 20 pollos, 15 arroces y 5 codillos al stock actual."*

### 6.2. Toma de Pedidos de Clientes (A Domicilio / Recoger)
* Los clientes escribirán al WhatsApp de la tienda.
* La IA actuará como recepcionista virtual. Conocerá el menú del día y el stock en tiempo real.
* Tomará nota del pedido, validará si es a domicilio o para recoger, y pedirá la dirección si es necesario.
* Inyectará el pedido en la base de datos de la TPV en estado `PENDIENTE`.

---

## 🔵 FASE 7: PASARELA DE PAGOS Y CONTROL REMOTO (DÍA 10)

**Objetivo:** Permitir el cobro sin fricción y el control físico de la tienda (caja registradora) desde cualquier parte del mundo.

### 7.1. Pasarela de Pagos (Stripe)
* Al finalizar la toma del pedido por WhatsApp, la IA generará un enlace de pago único y seguro a través de Stripe Checkout.
* El cliente podrá pagar con Tarjeta, Apple Pay o Google Pay.
* Un Webhook en Render interceptará el pago exitoso y cambiará el pedido a `PAGADO` automáticamente, disparando la impresión en la cocina.

### 7.2. Control Remoto de Hardware (Admin Móvil)
* El administrador podrá entrar al Dashboard web (`/dashboard`) desde su teléfono móvil.
* Un botón gigante de **"ABRIR CAJA"** enviará una señal a través del túnel inverso (Long-Polling) directamente a la tablet Android de la tienda.
* La tablet transmitirá el código binario ESC/POS (`\x1B\x70...`) al cajón portamonedas para que se abra mágicamente, sin importar dónde esté el administrador.

---

> [!IMPORTANT]
> **PROTOCOLO DE DESARROLLO PARA IA's:**
> Cualquier agente de IA que trabaje en este proyecto DEBE leer este documento y ejecutar estrictamente la fase correspondiente SIN saltarse pasos ni romper los endpoints de las Fases anteriores. Se debe priorizar el **100% Offline-First** para la operativa de ventas. La conexión a Internet solo debe ser obligatoria para enviar el WhatsApp de cierre o sincronizar backups.
