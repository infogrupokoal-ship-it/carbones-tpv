from .user import Usuario, Fichaje
from .product import Categoria, Producto, Proveedor, Ingrediente, Receta
from .order import Cliente, Pedido, ItemPedido, MovimientoStock
from .audit import AuditLog, ReporteZ, HardwareCommand

# Exportamos todos los modelos para que Base.metadata los registre
__all__ = [
    "Usuario", "Fichaje",
    "Categoria", "Producto", "Proveedor", "Ingrediente", "Receta",
    "Cliente", "Pedido", "ItemPedido", "MovimientoStock",
    "AuditLog", "ReporteZ", "HardwareCommand"
]
