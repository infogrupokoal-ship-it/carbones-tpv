import uvicorn
from fastapi import FastAPI, Request
import json
import logging
import os
import sys
from datetime import datetime

# Dependencias para imprimir en Windows (Asegúrate de instalarlas: pip install pypiwin32)
try:
    import win32print
    import win32ui
    PRINT_ENABLED = True
except ImportError:
    PRINT_ENABLED = False
    print("Advertencia: No se encontraron librerías de impresión de Windows. Usa 'pip install pypiwin32'")

app = FastAPI(title="Cargones y Pollos - Puente de Impresión Local")

# ------------------------------------------------------------
# CONFIGURACIÓN: Nombra tu impresora térmica exactamente 
# como aparece en "Dispositivos e impresoras" de Windows.
# ------------------------------------------------------------
NOMBRE_IMPRESORA_TICKET = "POS-80" 
NOMBRE_IMPRESORA_COCINA = "POS-80" # Puede ser otra diferente si tienes 2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def imprimir_texto_crudo(nombre_impresora, texto_ticket):
    """Envía texto crudo (ESC/POS) o texto normal a la impresora térmica"""
    if not PRINT_ENABLED:
         logging.info("SIMULANDO IMPRESIÓN (Librerías win32print no instaladas):")
         logging.info(f"=== TICKET PARA {nombre_impresora} ==\n{texto_ticket}\n====================")
         return True

    try:
        hPrinter = win32print.OpenPrinter(nombre_impresora)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket Restaurante", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # Convertimos a bytes (Generalmente cp850 o utf-8 funciona para tildes en tickets)
                # Comando para cortar papel ESC/POS (opcional si la impresora está en crudo): b'\x1d\x56\x42\x00'
                datos = texto_ticket.encode('utf-8') 
                corte_papel = b'\n\n\n\n\x1B\x6D' # Hex code básico para corte de papel
                
                win32print.WritePrinter(hPrinter, datos + corte_papel)
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True
    except Exception as e:
        logging.error(f"Error al imprimir: {e}")
        return False

@app.post("/webhook/imprimir")
async def recibir_ticket(request: Request):
    """
    Este es el endpoint seguro que Ngrok expondrá.
    El VPS de la IA mandará un POST aquí con los datos del pedido.
    """
    payload = await request.json()
    
    tipo_ticket = payload.get("tipo", "cliente") # "cliente" o "cocina"
    numero_ticket = payload.get("numero_ticket", "T-00")
    origen = payload.get("origen", "MOSTRADOR")
    items = payload.get("items", [])
    total = payload.get("total", 0.0)
    
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # ---- MAQUETAR EL TICKET (Rollo de 80mm) ----
    linea = "-" * 40
    
    ticket =  "       CARBONES Y POLLOS       \n"
    ticket += "      Los mejores asados       \n\n"
    ticket += f"Ticket: {numero_ticket}\n"
    ticket += f"Fecha: {fecha_str}\n"
    ticket += f"Origen: {origen}\n"
    ticket += linea + "\n"
    ticket += "Cant  Producto             Precio\n"
    ticket += linea + "\n"
    
    for item in items:
        # Formatear columnas (Cant. fija a 4, nombre cortado a 18, precio)
        cant = str(item.get("cantidad", 1)).ljust(4)
        nomb = str(item.get("nombre", "")[:18]).ljust(18)
        prec = f"{item.get('precio', 0.0):.2f}€".rjust(8)
        ticket += f"{cant} {nomb}    {prec}\n"
        
    ticket += linea + "\n"
    ticket += f"TOTAL A PAGAR:             {total:.2f}€\n".rjust(40)
    ticket += linea + "\n"
    
    if tipo_ticket == "cliente":
        ticket += "      Gracias por su visita!    \n\n\n"
        impresora_destino = NOMBRE_IMPRESORA_TICKET
    else:
        ticket += "           *** COCINA ***       \n\n\n"
        impresora_destino = NOMBRE_IMPRESORA_COCINA

    # Mandar a la impresora fìsica
    exito = imprimir_texto_crudo(impresora_destino, ticket)
    
    if exito:
        return {"status": "ok", "msj": f"Impreso en {impresora_destino}"}
    else:
        return {"status": "error", "msj": "Fallo en la impresora local"}

if __name__ == "__main__":
    print("\n--- SERVIDOR DE IMPRESION LOCAL (PUENTE) INICIADO ---")
    print("Recuerda abrir Ngrok con: ngrok http 8000")
    print("------------------------------------------------------\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
