import time
import requests
import json
import logging
from datetime import datetime
import sys

# Configuración
API_BASE = "http://113.30.148.104:5001/api/hardware"
NOMBRE_IMPRESORA_TICKET = "POS-80" 
NOMBRE_IMPRESORA_COCINA = "POS-80"
POLL_INTERVAL = 2 # Segundos

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Windows Printing
try:
    import win32print
    import win32ui
    PRINT_ENABLED = True
except ImportError:
    PRINT_ENABLED = False
    logging.warning("No se encontraron librerías de impresión de Windows. Usa 'pip install pypiwin32'")

def imprimir_texto_crudo(nombre_impresora, texto_ticket):
    """Envía texto crudo (ESC/POS) a la impresora térmica en Windows"""
    if PRINT_ENABLED:
        try:
            hprinter = win32print.OpenPrinter(nombre_impresora)
            try:
                win32print.StartDocPrinter(hprinter, 1, ("Ticket TPV", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, texto_ticket.encode("cp850", errors="ignore"))
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                logging.info(f"TICKET IMPRESO EN: {nombre_impresora}")
                return True
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            logging.error(f"Error imprimiendo: {e}")
            return False
    return False

def abrir_cajon():
    secuencia_apertura = "\x1B\x70\x00\x19\xFA"
    return imprimir_texto_crudo(NOMBRE_IMPRESORA_TICKET, secuencia_apertura)

def formato_ticket(payload):
    tipo_ticket = payload.get("tipo", "cliente")
    numero_ticket = payload.get("numero_ticket", "T-00")
    origen = payload.get("origen", "MOSTRADOR")
    items = payload.get("items", [])
    total = payload.get("total", 0.0)
    
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    linea = "-" * 40
    ticket = ""
    
    if tipo_ticket == "cliente":
        ticket += "      CARBONES Y POLLOS       \n"
        ticket += "      Los mejores asados      \n"
        ticket += "   NIF: B-12345678  Dir: Falsa 123\n\n"
        ticket += "      FACTURA SIMPLIFICADA    \n"
        ticket += f"Ticket: {numero_ticket}\n"
        ticket += f"Fecha: {fecha_str}\n"
        ticket += f"Atiende: {origen}\n"
        ticket += linea + "\n"
        ticket += "Cant  Producto             Precio\n"
        ticket += linea + "\n"
        
        for item in items:
            cant = str(item.get("cantidad", 1)).ljust(4)
            nomb = str(item.get("nombre", ""))[:18].ljust(18)
            prec = f"{item.get('precio', 0.0):.2f}€".rjust(8)
            ticket += f"{cant} {nomb}    {prec}\n"
            
        ticket += linea + "\n"
        ticket += f"TOTAL A PAGAR:             {total:.2f}€\n".rjust(40)
        ticket += "\n" + linea + "\n"
        ticket += "      Gracias por su visita!    \n\n\n\n\n"
        return ticket, NOMBRE_IMPRESORA_TICKET
        
    else:
        # Ticket Cocina
        ticket += "           *** COCINA ***       \n\n"
        ticket += f"COMANDA: {numero_ticket}\n"
        ticket += f"HORA: {fecha_str}\n"
        ticket += f"ORIGEN: {origen}\n"
        ticket += "=" * 40 + "\n"
        
        for item in items:
            cant = str(item.get("cantidad", 1))
            nomb = str(item.get("nombre", ""))
            ticket += f"[ {cant} ] {nomb.upper()}\n"
            
        ticket += "=" * 40 + "\n\n\n\n\n"
        return ticket, NOMBRE_IMPRESORA_COCINA

def process_command(cmd):
    cmd_id = cmd.get("id")
    accion = cmd.get("accion")
    payload = cmd.get("payload", {})
    
    logging.info(f"Procesando Comando #{cmd_id} -> {accion}")
    
    exito = False
    if accion == "abrir_caja":
        exito = abrir_cajon()
    elif accion == "imprimir":
        if payload:
            texto, impresora = formato_ticket(payload)
            exito = imprimir_texto_crudo(impresora, texto)
        else:
            logging.error("Comando imprimir sin payload")
            
    # Marcar como ejecutado independientemente de si falló la impresora física
    # (Para no bloquear la cola)
    try:
        requests.post(f"{API_BASE}/ack/{cmd_id}", timeout=5)
        logging.info(f"Comando #{cmd_id} marcado como ACK en el servidor")
    except Exception as e:
        logging.error(f"Error enviando ACK al servidor: {e}")

def run_agent():
    logging.info("========================================")
    logging.info("=  AGENTE HARDWARE TPV (POLL CLIENT)   =")
    logging.info("========================================")
    logging.info(f"Conectando a VPS: {API_BASE}")
    
    while True:
        try:
            res = requests.get(f"{API_BASE}/poll", timeout=5)
            if res.status_code == 200:
                data = res.json()
                comandos = data.get("comandos", [])
                for cmd in comandos:
                    process_command(cmd)
        except requests.exceptions.RequestException as e:
            # Silence connection errors to avoid spamming the console on network drops
            pass
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_agent()
