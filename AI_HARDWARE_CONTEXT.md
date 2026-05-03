# AI HARDWARE CONTEXT

## Topología de Red Física del Local

### Router Principal
- **Modelo:** TP-Link Omada ER605 Gigabit VPN Gateway.
- **IP Base:** `192.168.0.1`
- **Función:** Asignar IPs estáticas a las impresoras y al servidor TPV (ordenador Windows) para poder recibir impresión directa por socket TCP/IP (puerto 9100).

### Impresora 1: Cocina (Tickets de marcha)
- **Modelo:** URAPOS / UROVO DP1201-UBK.
- **Tecnología:** Thermal Receipt Printer (58mm/80mm, recomendada 80mm en cocina).
- **Conectividad:** Ethernet / USB / Serial.
- **Protocolo:** ESC/POS.
- **Energía:** 24V 2A.
- **Uso:** Recibir comandos desde la nube (Render) a través del proxy local, y trocear e imprimir comandas grandes con ruido o señal acústica.

### Impresora 2: Mostrador / Cliente
- **Modelo:** DISH EC-Q3-58 (o similar genérica china).
- **Tecnología:** Thermal Receipt Printer (Probablemente 58mm).
- **Uso:** Impresión del recibo final del cliente y tickets resumen de caja (Z).

## Comandos de Diagnóstico (Windows TPV Local)
Si se pierde conexión con las impresoras, usar la PowerShell del Kiosko físico:

1. **Verificar IP del Kiosko:**
   `ipconfig`
2. **Escanear Red / Ver IPs Asignadas:**
   `arp -a`
3. **Verificar que el Router Responde:**
   `ping 192.168.0.1`
4. **Comprobar Puerto 9100 (ESC/POS) de Impresora:**
   `Test-NetConnection 192.168.0.XXX -Port 9100`

## Conexión Nube <-> Local (El Proxy)
Dado que Render (Nube) no puede ver la `192.168.0.XXX`, el ecosistema usa un programa intermedio: `local_printer_bridge.py`.
Este script corre en el Windows de la tienda, expone un servidor en el puerto 8080 en `localhost`, o hace "Long Polling" hacia la nube para extraer los tickets pendientes e imprimirlos por LAN.
Las variables requeridas para esto en la nube son:
- `PRINTER_KITCHEN_HOST`
- `PRINTER_RECEIPT_HOST`
- `LOCAL_PRINTER_URL`
