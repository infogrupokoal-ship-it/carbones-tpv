from datetime import datetime
import socket
import logging


class TicketFormatter:
    """Clase centralizada para el formateo de tickets ESC/POS."""

    LINE_WIDTH = 40
    DIVIDER = "-" * LINE_WIDTH
    DOUBLE_DIVIDER = "=" * LINE_WIDTH

    @classmethod
    def format_client_ticket(cls, data: dict) -> str:
        """Genera el texto para el ticket de entrega al cliente."""
        numero = data.get("numero_ticket", "T-00")
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        origen = data.get("origen", "MOSTRADOR")
        items = data.get("items", [])
        total = data.get("total", 0.0)

        ticket = []
        ticket.append("      CARBONES Y POLLOS       ")
        ticket.append("      Los mejores asados       ")
        ticket.append("   NIF: B-12345678  Dir: Falsa 123\n")
        ticket.append("      FACTURA SIMPLIFICADA    ")
        ticket.append(f"Ticket: {numero}")
        ticket.append(f"Fecha: {fecha}")
        ticket.append(f"Atiende: {origen}")
        ticket.append(cls.DIVIDER)
        ticket.append("Cant  Producto             Precio")
        ticket.append(cls.DIVIDER)

        for it in items:
            cant = str(it.get("cantidad", 1)).ljust(4)
            nomb = str(it.get("nombre", ""))[:18].ljust(18)
            prec = f"{it.get('precio', 0.0):.2f}€".rjust(8)
            ticket.append(f"{cant} {nomb}    {prec}")

        ticket.append(cls.DIVIDER)
        ticket.append(f"TOTAL A PAGAR:             {total:.2f}€".rjust(cls.LINE_WIDTH))

        # Desglose Fiscal
        ticket.append("\nDesglose de Impuestos (IVA INC):")
        ticket.append("Tipo      Base Imp       Cuota")
        b10 = data.get("base_imponible_10", 0.0)
        c10 = data.get("cuota_iva_10", 0.0)
        if b10 > 0:
            ticket.append(f"10%       {b10:.2f}€".ljust(22) + f"{c10:.2f}€".rjust(8))

        b21 = data.get("base_imponible_21", 0.0)
        c21 = data.get("cuota_iva_21", 0.0)
        if b21 > 0:
            ticket.append(f"21%       {b21:.2f}€".ljust(22) + f"{c21:.2f}€".rjust(8))

        ticket.append(cls.DIVIDER)
        ticket.append("      Gracias por su visita!    \n\n\n")
        return "\n".join(ticket)

    @classmethod
    def format_kitchen_ticket(cls, data: dict) -> str:
        """Genera el texto para el ticket de preparación en cocina."""
        numero = data.get("numero_ticket", "T-00")
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        origen = data.get("origen", "MOSTRADOR")
        items = data.get("items", [])
        notas = data.get("notas_cliente", "")

        ticket = []
        ticket.append("           *** COCINA ***       \n")
        ticket.append(f"COMANDA: {numero}")
        ticket.append(f"HORA: {fecha}")
        ticket.append(f"ORIGEN: {origen}")
        ticket.append(cls.DOUBLE_DIVIDER)

        for it in items:
            cant = it.get("cantidad", 1)
            nomb = it.get("nombre", "").upper()
            ticket.append(f"[ {cant} ] {nomb}")

        if notas:
            ticket.append("\n" + "*" * cls.LINE_WIDTH)
            ticket.append("!!! NOTAS DEL CLIENTE !!!")
            ticket.append(notas.upper())
            ticket.append("*" * cls.LINE_WIDTH + "\n")

        ticket.append(cls.DOUBLE_DIVIDER + "\n\n\n")
        return "\n".join(ticket)

logger = logging.getLogger(__name__)

class EscPosPrinter:
    """
    Capa de abstracción de hardware para impresoras térmicas ESC/POS.
    Permite enviar tickets de comanda y facturas simplificadas a través de red (TCP/IP).
    """
    
    # Comandos ESC/POS Básicos
    ESC = b'\x1b'
    GS = b'\x1d'
    INITIALIZE = ESC + b'@'
    CUT_PAPER = GS + b'V\x00'
    LF = b'\n'

    def __init__(self, host: str, port: int = 9100, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_raw(self, data: bytes) -> bool:
        """
        Envía bytes crudos a la impresora por socket.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                s.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Error imprimiendo en {self.host}:{self.port} - {e}")
            return False

    def print_ticket(self, formatted_text: str) -> bool:
        """
        Toma texto formateado y lo envía a la impresora con comandos básicos.
        """
        payload = self.INITIALIZE
        # cp850 commonly used for European POS
        payload += formatted_text.encode('cp850', errors='replace') 
        payload += self.LF * 4
        payload += self.CUT_PAPER
        return self.send_raw(payload)

# Singleton helper
_default_printer = None

def get_printer(host="192.168.1.200") -> EscPosPrinter:
    global _default_printer
    if not _default_printer:
        _default_printer = EscPosPrinter(host=host)
    return _default_printer
