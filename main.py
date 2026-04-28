import uvicorn
import socket
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()
import requests
# from ai_engine import procesar_mensaje_whatsapp

from models import Base, Categoria, Producto, Pedido, ItemPedido, MovimientoStock, ReporteZ, Cliente

app = FastAPI(title="Cargones y Pollos TPV API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "sqlite:///tpv_data.sqlite"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    # Seeding automatico al arrancar (Critico para entornos efimeros como Render)
    try:
        import fractional_seeder
        fractional_seeder.seed()
    except Exception as e:
        print("Error durante el auto-seeding:", e)

# Pydantic Schemas
class ItemCrear(BaseModel):
    producto_id: str
    cantidad: int

class PedidoCrear(BaseModel):
    items: List[ItemCrear]
    origen: str = "QUIOSCO"
    estado_inicial: str = "ESPERANDO_PAGO"
    cubiertos_qty: int = 0
    notas_cliente: Optional[str] = None
    canjear_puntos: bool = False

class ProduccionCrear(BaseModel):
    producto_id: str
    cantidad: int
    descripcion: str = "Producción manual"

class ReviewCrear(BaseModel):
    pedido_id: Optional[str] = None
    cliente_id: Optional[str] = None
    rating: int
    comentario: Optional[str] = None

class FichajeRequest(BaseModel):
    pin: str
    tipo: str # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA

class PedidoProveedorRequest(BaseModel):
    ingrediente_id: str
    cantidad: float

class CheckoutRequest(BaseModel):
    metodo_pago: str = "EFECTIVO" # EFECTIVO, TARJETA, MAQUINA

class UbicacionRequest(BaseModel):
    lat: float
    lon: float
    distancia_metros: Optional[float] = None

import base64
from fastapi.responses import RedirectResponse
# --- ENDPOINTS REST ---

@app.get("/api/auth/magic_login")
def magic_login(token: str, db: Session = Depends(get_db)):
    try:
        wa_id = base64.b64decode(token).decode('utf-8')
        cliente = db.query(Cliente).filter(Cliente.wa_id == wa_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Redirigimos al B2C pasándole el token y el id de cliente
        response = RedirectResponse(url=f"/static/registro_cliente.html?token={token}&cliente_id={cliente.id}")
        response.set_cookie(key="b2c_token", value=token, httponly=False) # Simplificado para JS
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail="Token inválido")

@app.get("/api/productos")
def listar_productos(db: Session = Depends(get_db)):
    prods = db.query(Producto).filter(Producto.is_active == True).all()
    # Logica fraccional: Sobrescribir stock_actual visual de hijos (ej. Cuarto Pollo) en base a lo que tenga el stock_base_id (Pollo generico)
    for p in prods:
        if p.stock_base_id:
            parent = db.query(Producto).get(p.stock_base_id)
            if parent and p.factor_stock > 0:
                p.stock_actual = int(parent.stock_actual / p.factor_stock)

    # Regla: No mostrar carta de bocadillos hasta las 17:00
    if datetime.now().hour < 17:
        categorias_manana = db.query(Categoria).filter(Categoria.nombre.in_(["Pollos Asados", "Guarniciones", "Bebidas"])).all()
        ids_permitidos = [c.id for c in categorias_manana]
        prods = [p for p in prods if p.categoria_id in ids_permitidos]
    return prods

@app.get("/api/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    cats = db.query(Categoria).order_by(Categoria.orden).all()
    # Regla: No mostrar carta de bocadillos hasta las 17:00
    if datetime.now().hour < 17:
        cats = [c for c in cats if c.nombre in ["Pollos Asados", "Guarniciones", "Bebidas"]]
    return cats

# --- ENDPOINTS RRHH (Fichajes) ---
@app.post("/api/rrhh/fichar")
def registrar_fichaje(req: FichajeRequest, db: Session = Depends(get_db)):
    from models import Usuario, Fichaje
    user = db.query(Usuario).filter(Usuario.password == req.pin).first()
    if not user:
        raise HTTPException(status_code=403, detail="PIN incorrecto")
        
    fichaje = Fichaje(usuario_id=user.id, tipo=req.tipo)
    db.add(fichaje)
    db.commit()
    return {"status": "ok", "msj": f"Fichaje ({req.tipo}) registrado para {user.username}", "fecha": fichaje.fecha.isoformat()}

@app.get("/api/rrhh/fichajes")
def listar_fichajes(db: Session = Depends(get_db)):
    from models import Fichaje, Usuario
    fichajes = db.query(Fichaje).order_by(Fichaje.fecha.desc()).limit(50).all()
    out = []
    for f in fichajes:
        u = db.query(Usuario).get(f.usuario_id)
        out.append({
            "id": f.id,
            "username": u.username if u else "Desconocido",
            "tipo": f.tipo,
            "fecha": f.fecha.strftime("%d/%m %H:%M")
        })
    return out

# --- ENDPOINTS INVENTARIO (Proveedores) ---
@app.get("/api/inventario")
def listar_inventario(db: Session = Depends(get_db)):
    from models import Ingrediente, Proveedor
    ingredientes = db.query(Ingrediente).all()
    out = []
    for ing in ingredientes:
        prov = db.query(Proveedor).get(ing.proveedor_id) if ing.proveedor_id else None
        out.append({
            "id": ing.id,
            "nombre": ing.nombre,
            "stock_actual": ing.stock_actual,
            "stock_minimo": ing.stock_minimo,
            "unidad": ing.unidad_medida,
            "proveedor_nombre": prov.nombre if prov else "Sin Proveedor",
            "proveedor_email": prov.email if prov else ""
        })
    return out

@app.post("/api/inventario/pedido")
def realizar_pedido_proveedor(req: PedidoProveedorRequest, db: Session = Depends(get_db)):
    from models import Ingrediente, Proveedor
    ing = db.query(Ingrediente).get(req.ingrediente_id)
    if not ing: raise HTTPException(404, "Ingrediente no encontrado")
    
    prov = db.query(Proveedor).get(ing.proveedor_id)
    print(f"-> [PROVEEDOR SIMULADO] Pedido de {req.cantidad} {ing.unidad_medida} de {ing.nombre} a {prov.nombre if prov else 'Desconocido'}")
    
    # Auto-replenish MVP
    ing.stock_actual += req.cantidad
    db.commit()
    return {"status": "ok", "msj": f"Pedido enviado a {prov.nombre if prov else 'Proveedor'} y stock repuesto."}

@app.post("/api/pedidos")
def crear_pedido(pedido: PedidoCrear, cliente_id: Optional[str] = None, db: Session = Depends(get_db)):
    from models import Cliente
    
    # Intento buscar cliente si viene origen KIOSKO_TELEFONO por ejemplo, o si el request.origen trae "WHATSAPP-telefono"
    telefono_asociado = None
    if "-" in pedido.origen:
        origen_base, telefono_asociado = pedido.origen.split("-", 1)
    else:
        origen_base = pedido.origen
        
    cliente = None
    descuento_aplicado = 0.0
    
    if cliente_id:
        cliente = db.query(Cliente).get(cliente_id)
    elif telefono_asociado:
        cliente = db.query(Cliente).filter(Cliente.telefono == telefono_asociado).first()
        if not cliente:
            cliente = Cliente(telefono=telefono_asociado, nivel_fidelidad="BRONCE")
            db.add(cliente)
            db.flush()
            
    if cliente:
        if cliente.nivel_fidelidad == "PLATA": descuento_aplicado = 0.05
        elif cliente.nivel_fidelidad == "ORO": descuento_aplicado = 0.10
        
    nuevo_pedido = Pedido(
        numero_ticket=f"T-{(db.query(Pedido).count() % 100) + 1:02d}", 
        origen=origen_base, 
        estado=pedido.estado_inicial,
        cliente_id=cliente.id if cliente else None,
        cubiertos_qty=pedido.cubiertos_qty,
        notas_cliente=pedido.notas_cliente
    )
    db.add(nuevo_pedido)
    db.flush()
    
    # IVA Tracking
    total_iva_10 = 0.0
    total_iva_21 = 0.0

    total = 0.0
    
    # 1) Registrar cubiertos como un ítem contable al 10% IVA
    if pedido.cubiertos_qty > 0:
        coste_cubiertos = pedido.cubiertos_qty * 0.20
        total += coste_cubiertos
        total_iva_10 += coste_cubiertos
        # En el front-end y receipt se tratará como servicio genérico si no hay tabla Producto
        
    for item in pedido.items:
        prod = db.query(Producto).get(item.producto_id)
        if not prod: continue
        # Restar stock (Chequeo Fraccional)
        if prod.stock_base_id:
            parent = db.query(Producto).get(prod.stock_base_id)
            if parent:
                parent.stock_actual -= (item.cantidad * prod.factor_stock)
                db.add(MovimientoStock(producto_id=parent.id, cantidad=-(item.cantidad * prod.factor_stock), tipo="VENTA", origen_id=nuevo_pedido.id, descripcion=f"Venta (Ref: {prod.nombre})"))
                
                # FASE 4: Alerta Predictiva de Inventario
                if parent.stock_minimo > 0 and parent.stock_actual <= parent.stock_minimo:
                    alerta = f"🚨 *ALERTA DE STOCK* 🚨\nEl producto *{parent.nombre}* ha bajado del umbral crítico.\nStock actual: {parent.stock_actual}\n¡Repón inmediatamente!"
                    try:
                        requests.post(os.environ.get("WAHA_URL", "http://127.0.0.1:3000/api/sendText"), json={"chatId": "34604864187@c.us", "text": alerta, "session": "default"}, timeout=2)
                    except:
                        pass
        else:
            prod.stock_actual -= item.cantidad
            db.add(MovimientoStock(producto_id=prod.id, cantidad=-item.cantidad, tipo="VENTA", origen_id=nuevo_pedido.id, descripcion="Venta TPV"))
            
            # FASE 4: Alerta Predictiva de Inventario
            if prod.stock_minimo > 0 and prod.stock_actual <= prod.stock_minimo:
                alerta = f"🚨 *ALERTA DE STOCK* 🚨\nEl producto *{prod.nombre}* ha bajado del umbral crítico.\nStock actual: {prod.stock_actual}\n¡Haz pedido al proveedor!"
                try:
                    requests.post(os.environ.get("WAHA_URL", "http://127.0.0.1:3000/api/sendText"), json={"chatId": "34604864187@c.us", "text": alerta, "session": "default"}, timeout=2)
                except:
                    pass
            
        # Deducción de Ingredientes (Recetas)
        from models import Receta, Ingrediente
        recetas = db.query(Receta).filter(Receta.producto_id == prod.id).all()
        for receta in recetas:
            ing = db.query(Ingrediente).get(receta.ingrediente_id)
            if ing:
                ing.stock_actual -= (receta.cantidad_necesaria * item.cantidad)
                
                # FASE 4: Alerta Predictiva de Inventario (Ingredientes)
                if ing.stock_minimo > 0 and ing.stock_actual <= ing.stock_minimo:
                    alerta_ing = f"🚨 *ALERTA DE INGREDIENTE* 🚨\nEl ingrediente *{ing.nombre}* está bajo mínimo.\nStock actual: {ing.stock_actual} {ing.unidad_medida}\n¡Pide a tu proveedor!"
                    try:
                        requests.post(os.environ.get("WAHA_URL", "http://127.0.0.1:3000/api/sendText"), json={"chatId": "34604864187@c.us", "text": alerta_ing, "session": "default"}, timeout=2)
                    except:
                        pass
                        
        coste_item = prod.precio * item.cantidad
        total += coste_item
        
        # Desglose IVA
        if prod.impuesto == 21.0:
            total_iva_21 += coste_item
        else:
            total_iva_10 += coste_item # Por defecto 10% en asador
            
        db.add(ItemPedido(pedido_id=nuevo_pedido.id, producto_id=prod.id, cantidad=item.cantidad, precio_unitario=prod.precio))
        
    # Aplicar descuento de fidelidad
    subtotal = total
    if descuento_aplicado > 0:
        total = total - (total * descuento_aplicado)
        # Descuentos reducen IVA propocionalmente
        total_iva_10 = total_iva_10 * (1 - descuento_aplicado)
        total_iva_21 = total_iva_21 * (1 - descuento_aplicado)
        
    # Pollos-Coins: Canjeo
    if pedido.canjear_puntos and cliente and cliente.puntos_fidelidad >= 50:
        descuento_puntos = (cliente.puntos_fidelidad // 50) * 5.0 # 50 puntos = 5 euros
        if descuento_puntos > total:
            descuento_puntos = total
        
        total -= descuento_puntos
        cliente.puntos_fidelidad -= int((descuento_puntos / 5.0) * 50)
        
        # Reducir IVA proporcionalmente
        if subtotal > 0:
            proporcion_desc = descuento_puntos / subtotal
            total_iva_10 -= total_iva_10 * proporcion_desc
            total_iva_21 -= total_iva_21 * proporcion_desc
            
    # Pollos-Coins: Acumulación
    if cliente:
        cliente.puntos_fidelidad += int(total) # 1 punto por cada euro gastado
    
    nuevo_pedido.total = round(total, 2)
    nuevo_pedido.descuento_aplicado = descuento_aplicado
    
    # Bases e IVA
    nuevo_pedido.base_imponible_10 = round(total_iva_10 / 1.10, 2)
    nuevo_pedido.cuota_iva_10 = round(total_iva_10 - nuevo_pedido.base_imponible_10, 2)
    nuevo_pedido.base_imponible_21 = round(total_iva_21 / 1.21, 2)
    nuevo_pedido.cuota_iva_21 = round(total_iva_21 - nuevo_pedido.base_imponible_21, 2)
    
    # Send to kitchen immediately if it's already paid/confirmed
    if nuevo_pedido.estado == "EN_PREPARACION":
        from models import HardwareCommand
        import json
        
        items_payload = []
        for it in pedido.items:
            prod_obj = db.query(Producto).get(it.producto_id)
            if prod_obj:
                items_payload.append({"nombre": prod_obj.nombre, "cantidad": it.cantidad, "precio": prod_obj.precio * it.cantidad})
                
        payload = {
            "numero_ticket": nuevo_pedido.numero_ticket,
            "origen": nuevo_pedido.origen,
            "total": total,
            "items": items_payload,
            "base_imponible_10": nuevo_pedido.base_imponible_10,
            "cuota_iva_10": nuevo_pedido.cuota_iva_10,
            "base_imponible_21": nuevo_pedido.base_imponible_21,
            "cuota_iva_21": nuevo_pedido.cuota_iva_21,
            "notas_cliente": nuevo_pedido.notas_cliente,
            "tipo": "cocina"
        }
        db.add(HardwareCommand(accion="imprimir", origen="b2c_local", payload=json.dumps(payload)))
        payload["tipo"] = "cliente"
        db.add(HardwareCommand(accion="imprimir", origen="b2c_local", payload=json.dumps(payload)))

    db.commit()
    return {"status": "ok", "pedido_id": nuevo_pedido.id, "ticket": nuevo_pedido.numero_ticket, "total": total, "descuento": descuento_aplicado}

@app.get("/api/pedidos")
def listar_pedidos(estado: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Pedido)
    if estado:
        query = query.filter(Pedido.estado == estado)
    pedidos = query.order_by(Pedido.fecha.desc()).all()
    
    out = []
    for p in pedidos:
        items_out = []
        for it in p.items:
            prod = db.query(Producto).get(it.producto_id)
            if prod:
                items_out.append({
                    "id": it.id,
                    "cantidad": it.cantidad,
                    "precio_unitario": it.precio_unitario,
                    "producto": {
                        "id": prod.id,
                        "nombre": prod.nombre,
                        "alergenos": prod.alergenos,
                        "is_addon": prod.is_addon
                    }
                })
        
        out.append({
            "id": p.id,
            "numero_ticket": p.numero_ticket,
            "fecha": p.fecha.isoformat(),
            "estado": p.estado,
            "total": p.total,
            "origen": p.origen,
            "notas_cliente": p.notas_cliente,
            "items": items_out
        })
    return out

@app.get("/api/pedidos/{pedido_id}/items")
def ver_pedido_items(pedido_id: str, db: Session = Depends(get_db)):
    items = db.query(ItemPedido).options(joinedload(ItemPedido.pedido)).filter(ItemPedido.pedido_id == pedido_id).all()
    out = []
    for it in items:
        prod = db.query(Producto).get(it.producto_id)
        out.append({
            "id": it.id,
            "cantidad": it.cantidad,
            "precio": it.precio_unitario,
            "nombre": prod.nombre if prod else "Desconocido"
        })
    return out

@app.post("/api/pedidos/{pedido_id}/estado")
def actualizar_estado(pedido_id: str, estado: str, db: Session = Depends(get_db)):
    from models import Cliente, HardwareCommand, Producto, ItemPedido, Receta, Ingrediente, MovimientoStock
    import json
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
        
    estado_anterior = pedido.estado
    pedido.estado = estado
    
    # Enviar a cocina si acaba de ser confirmado el pago en caja local
    if estado == "EN_PREPARACION" and estado_anterior in ["ESPERANDO_PAGO", "ESPERANDO_PAGO_LOCAL"]:
        items_payload = []
        for it in pedido.items:
            prod_obj = db.query(Producto).get(it.producto_id)
            if prod_obj:
                items_payload.append({"nombre": prod_obj.nombre, "cantidad": it.cantidad, "precio": prod_obj.precio * it.cantidad})
        
        payload = {
            "numero_ticket": pedido.numero_ticket,
            "origen": pedido.origen,
            "total": pedido.total,
            "items": items_payload,
            "base_imponible_10": pedido.base_imponible_10,
            "cuota_iva_10": pedido.cuota_iva_10,
            "base_imponible_21": pedido.base_imponible_21,
            "cuota_iva_21": pedido.cuota_iva_21,
            "notas_cliente": pedido.notas_cliente,
            "tipo": "cocina"
        }
        db.add(HardwareCommand(accion="imprimir", origen="caja_confirmacion", payload=json.dumps(payload)))
    
    # Acciones extra si el pedido esta listo y viene de whatsapp -> Avisar
    if estado == "LISTO" and pedido.cliente_id:
        c = db.query(Cliente).get(pedido.cliente_id)
        if c:
             print(f"-> [WEBHOOK SIMULADO] IA enviando WhatsApp a {c.telefono}: '¡Tu pedido {pedido.numero_ticket} ya está listo y caliente!'")
             
    # FASE X5: Algoritmo de deducción fraccional (Escandallos) y Gamificación (Pollos-Coins) al completar pedido
    if estado == "COMPLETADO" and estado_anterior != "COMPLETADO":
        for it in pedido.items:
            recetas = db.query(Receta).filter(Receta.producto_id == it.producto_id).all()
            for r in recetas:
                ing = db.query(Ingrediente).get(r.ingrediente_id)
                if ing:
                    cantidad_a_restar = r.cantidad_necesaria * it.cantidad
                    ing.stock_actual -= cantidad_a_restar
                    # Registro opcional de merma/consumo
                    # db.add(MovimientoStock(producto_id=None, cantidad=-cantidad_a_restar, tipo="CONSUMO_RECETA", origen_id=pedido.id, descripcion=f"Consumo de {ing.nombre} para {pedido.numero_ticket}"))

        # Gamificación: Sumar Pollos-Coins (1€ = 1 Punto)
        if pedido.cliente_id:
            c = db.query(Cliente).get(pedido.cliente_id)
            if c:
                puntos_ganados = int(pedido.total)
                c.puntos_fidelidad += puntos_ganados
                c.visitas += 1
                
                # Nivel dinámico
                if c.puntos_fidelidad >= 500: c.nivel_fidelidad = "ORO"
                elif c.puntos_fidelidad >= 200: c.nivel_fidelidad = "PLATA"
             
    db.commit()
    return {"status": "ok", "nuevo_estado": pedido.estado}

@app.post("/api/pedidos/{pedido_id}/ubicacion")
def actualizar_ubicacion(pedido_id: str, ubi: UbicacionRequest, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    pedido.latitud_actual = ubi.lat
    pedido.longitud_actual = ubi.lon
    if ubi.distancia_metros is not None:
        pedido.distancia_metros = ubi.distancia_metros
        
    db.commit()
    return {"status": "ok", "msj": "Ubicación actualizada en tiempo real"}

@app.post("/api/pedidos/{pedido_id}/cobrar")
def cobrar_pedido(pedido_id: str, request: CheckoutRequest, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    pedido.estado = "EN_PREPARACION"
    pedido.metodo_pago = request.metodo_pago
    db.commit()
    # Encolar comandos de hardware en vez de hacer POST HTTP a Ngrok
    import json
    try:
        items = []
        if pedido.cubiertos_qty > 0:
            items.append({"nombre": "Servicio Cubiertos", "cantidad": pedido.cubiertos_qty, "precio": 0.20 * pedido.cubiertos_qty})
            
        for db_it in pedido.items:
            prod = db.query(Producto).get(db_it.producto_id)
            items.append({"nombre": prod.nombre if prod else "Desconocido", "cantidad": db_it.cantidad, "precio": db_it.precio_unitario * db_it.cantidad})
            
        payload = {
            "numero_ticket": pedido.numero_ticket,
            "origen": pedido.origen,
            "total": pedido.total,
            "items": items,
            "base_imponible_10": pedido.base_imponible_10,
            "cuota_iva_10": pedido.cuota_iva_10,
            "base_imponible_21": pedido.base_imponible_21,
            "cuota_iva_21": pedido.cuota_iva_21,
            "notas_cliente": pedido.notas_cliente
        }
        
        # 1. Comando abrir caja
        db.add(HardwareCommand(accion="abrir_caja", origen="cobro_tpv"))
        # 2. Comando imprimir cocina
        payload["tipo"] = "cocina"
        db.add(HardwareCommand(accion="imprimir", origen="cobro_tpv", payload=json.dumps(payload)))
        # 3. Comando imprimir cliente
        payload["tipo"] = "cliente"
        db.add(HardwareCommand(accion="imprimir", origen="cobro_tpv", payload=json.dumps(payload)))
        
        db.commit()
    except Exception as e:
        print(f"Error encolando hardware: {e}")
        
    return {"status": "ok", "msj": "Pago Aprobado. Comandos encolados para la Tienda."}

@app.post("/api/webhook/caja_automatica")
def webhook_caja_automatica(payload: dict, db: Session = Depends(get_db)):
    # Este es el endpoint futuro para enganchar a tu hardware de cobro
    ticket = payload.get("numero_ticket")
    if ticket:
         p = db.query(Pedido).filter(Pedido.numero_ticket == ticket).first()
         if p and p.estado == "ESPERANDO_PAGO":
              p.estado = "EN_PREPARACION"
              p.metodo_pago = "MAQUINA"
              db.commit()
              return {"status": "cobrado"}
    return {"status": "ignorado"}

@app.post("/api/produccion")
def registrar_produccion(prod: ProduccionCrear, db: Session = Depends(get_db)):
    p = db.query(Producto).get(prod.producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    
    # Sumar stock (Fraccional vs Normal)
    if p.stock_base_id:
        parent = db.query(Producto).get(p.stock_base_id)
        parent.stock_actual += (prod.cantidad * p.factor_stock)
        db.add(MovimientoStock(producto_id=parent.id, cantidad=(prod.cantidad * p.factor_stock), tipo="PRODUCCION", descripcion=prod.descripcion))
        db.commit()
        return {"status": "ok", "nuevo_stock": int(parent.stock_actual / p.factor_stock)}
    else:
        p.stock_actual += prod.cantidad
        db.add(MovimientoStock(producto_id=p.id, cantidad=prod.cantidad, tipo="PRODUCCION", descripcion=prod.descripcion))
        db.commit()
        return {"status": "ok", "nuevo_stock": p.stock_actual}

@app.get("/api/inventario")
def ver_inventario(db: Session = Depends(get_db)):
    # Mostrar solo productos base (sin stock_base_id) o productos relevantes
    prods = db.query(Producto).filter(Producto.is_active == True, Producto.stock_base_id == None).all()
    out = []
    for p in prods:
        out.append({
            "id": p.id,
            "nombre": p.nombre,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo
        })
    return out

@app.get("/api/inventario/balance_hoy")
def balance_inventario_hoy(db: Session = Depends(get_db)):
    from datetime import datetime, date
    hoy = date.today()
    movs = db.query(MovimientoStock).all()
    productos = db.query(Producto).all()
    
    balance = {}
    for p in productos:
        balance[p.id] = {
            "sobrante_ayer": 0,
            "prod_manana": 0,
            "prod_tarde": 0,
            "ventas": 0,
            "mermas": 0,
            "ajustes": 0,
            "stock_actual": p.stock_actual
        }

    for m in movs:
        if m.fecha.date() == hoy:
            pid = m.producto_id
            if pid in balance:
                tipo = m.tipo
                cant = m.cantidad
                if tipo == "PRODUCCION_MANANA": balance[pid]["prod_manana"] += cant
                elif tipo == "PRODUCCION_TARDE": balance[pid]["prod_tarde"] += cant
                elif tipo == "MERMA": balance[pid]["mermas"] += abs(cant)
                elif tipo == "VENTA": balance[pid]["ventas"] += abs(cant)
                else: balance[pid]["ajustes"] += cant
    
    # Calcular sobrante de ayer matemáticamente
    for pid, b in balance.items():
        movimientos_hoy = b["prod_manana"] + b["prod_tarde"] - b["ventas"] - b["mermas"] + b["ajustes"]
        b["sobrante_ayer"] = b["stock_actual"] - movimientos_hoy
            
    return balance

class AjusteInventario(BaseModel):
    producto_id: str
    cantidad_ajuste: float
    descripcion: str = "Ajuste manual"
    tipo: str = "AJUSTE" # PRODUCCION_MANANA, PRODUCCION_TARDE, MERMA, SOBRANTE_DIA_ANTERIOR

@app.post("/api/inventario/ajuste")
def ajustar_inventario(req: AjusteInventario, db: Session = Depends(get_db)):
    p = db.query(Producto).get(req.producto_id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    
    # Si es MERMA, debe restar al stock actual
    if req.tipo == "MERMA" and req.cantidad_ajuste > 0:
        req.cantidad_ajuste = -req.cantidad_ajuste
        
    p.stock_actual += req.cantidad_ajuste
    db.add(MovimientoStock(producto_id=p.id, cantidad=req.cantidad_ajuste, tipo=req.tipo, descripcion=req.descripcion))
    db.commit()
    return {"status": "ok", "msj": f"Stock actualizado a {p.stock_actual}"}


# --- AUTH & DASHBOARD ---
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    from models import Usuario
    user = db.query(Usuario).filter(Usuario.username == req.username, Usuario.password == req.password).first()
    if not user:
        raise HTTPException(401, "Credenciales incorrectas")
    return {"status": "ok", "role": user.rol, "username": user.username}

@app.get("/api/dashboard")
def view_dashboard(turno: str = None, db: Session = Depends(get_db)):
    # Retorna la suma de Pedidos PAGADOS / PENDIENTES o posteriores
    # Si turno="manana", suma pedidos < 17:00 del dIa de hoy
    # Si turno="tarde", suma pedidos >= 17:00 del dIa de hoy
    hoy = datetime.now()
    pedidos = db.query(Pedido).filter(Pedido.estado != "ESPERANDO_PAGO").all()
    
    total = 0.0
    for p in pedidos:
        if p.fecha.date() == hoy.date():
            if turno == "manana" and p.fecha.hour < 17:
                total += p.total
            elif turno == "tarde" and p.fecha.hour >= 17:
                total += p.total
            elif not turno:
                total += p.total
    
    return {"total_facturado": total, "fecha": str(hoy.date()), "turno": turno or "todo"}

@app.get("/api/info")
def get_info():
    # Detect local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return {"ip_local": IP, "port": 5001}

# --- WEBHOOK WHATSAPP ---
TELEFONOS_RESPONSABLES = ["34600123456", "34688888888"] # <-- AQUI VAN LOS TLF DE LOS COCINEROS Y TUYOS
WHATSAPP_TOKEN_VERIFY = "grupo_koal_carbones_token_33"

@app.get("/webhook/whatsapp")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == WHATSAPP_TOKEN_VERIFY:
            return int(challenge)
        raise HTTPException(403, "Token invalido")
    raise HTTPException(400, "Bad Request")

@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    try:
        # Extraer el body asumiendo estandar de Meta API v16+
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    for msg in value["messages"]:
                        sender_phone = msg.get("from")
                        text = msg.get("text", {}).get("body", "")
                        
                        if text:
                            # Mandar a procesar al cerebro IA (Desactivado en nodo local TPV)
                            # respuesta_ia = procesar_mensaje_whatsapp(db, sender_phone, text, TELEFONOS_RESPONSABLES)
                            respuesta_ia = "IA desactivada en TPV local. Procesamiento movido a VPS."
                            
                            # AQUI EN PRODUCTIVO SE LLAMARÍA A LA API DE META PARA ENVIAR 'respuesta_ia' DE VUELTA.
                            # Ej: enviar_mensaje_meta(sender_phone, respuesta_ia)
                            # Para modo local y de prueba, lo imprimimos.
                            print(f"[{sender_phone}] -> IA DICE: {respuesta_ia}")
                            
        return {"status": "ok"}
    except Exception as e:
        print("Webhook Error:", e)
        return {"status": "error"}

# --- OFFLINE-FIRST SYNC ---
@app.post("/api/sync/push")
async def sync_push(request: Request, db: Session = Depends(get_db)):
    """ Recibe datos desde el nodo local y los guarda/actualiza en el Cloud. """
    payload = await request.json()
    pedidos = payload.get("pedidos", [])
    
    upserts = 0
    from datetime import datetime
    for p_data in pedidos:
        num_ticket = p_data.get("numero_ticket")
        if not num_ticket: continue
        
        # Check si ya existe el pedido
        existente = db.query(Pedido).filter(Pedido.numero_ticket == num_ticket).first()
        if existente:
            continue
            
        # Parse fecha
        fecha_str = p_data.get("fecha", "")
        parsed_fecha = datetime.now()
        try:
            # Simple conversion from YYYY-MM-DD HH:MM:SS.mmmmmm
            parsed_fecha = datetime.strptime(fecha_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        except:
             pass

        nuevo_pedido = Pedido(
            numero_ticket=num_ticket,
            origen=p_data.get("origen", "LOCAL"),
            total=p_data.get("total", 0.0),
            estado=p_data.get("estado", "LISTO"),
            metodo_pago=p_data.get("metodo_pago"),
            descuento_aplicado=p_data.get("descuento_aplicado", 0.0),
            cajero_username=p_data.get("cajero_username"),
            base_imponible_10=p_data.get("base_imponible_10", 0.0),
            cuota_iva_10=p_data.get("cuota_iva_10", 0.0),
            base_imponible_21=p_data.get("base_imponible_21", 0.0),
            cuota_iva_21=p_data.get("cuota_iva_21", 0.0),
            fecha=parsed_fecha,
            is_synced=True
        )
        db.add(nuevo_pedido)
        db.flush() # Force ID generation
        
        # Procesar Items
        items = p_data.get("items", [])
        for it in items:
            nuevo_item = ItemPedido(
                pedido_id=nuevo_pedido.id,
                producto_id=it.get("producto_id"),
                cantidad=it.get("cantidad", 1),
                precio_unitario=it.get("precio_unitario", 0.0),
                is_synced=True
            )
            db.add(nuevo_item)
            
        upserts += 1

    try:
        db.commit()
        return {"status": "ok", "msj": f"Sincronizados {upserts} pedidos fiscales correctamente."}
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=f"Error Sync PUSH: {str(e)}")

@app.get("/api/sync/pull")
def sync_pull(db: Session = Depends(get_db)):
    """ Devuelve datos que hayan sido creados en el Cloud y no estén en el Local. """
    from models import Pedido
    pedidos_nuevos = db.query(Pedido).filter(Pedido.is_synced == False, Pedido.origen == "WHATSAPP").all()
    out = []
    for p in pedidos_nuevos:
        out.append({
            "id": p.id,
            "numero_ticket": p.numero_ticket,
            "total": p.total,
            # Marcar aquí o esperar confirmación
        })
        p.is_synced = True
    db.commit()
    return {"status": "ok", "nuevos_pedidos": out}

# --- CLOUD-EDGE HARDWARE BRIDGE ---
from models import HardwareCommand

@app.post("/api/hardware/enqueue")
async def hw_enqueue(request: Request, db: Session = Depends(get_db)):
    """El sistema pide ejecutar una acción física (cajón, ticket) en la tienda."""
    data = await request.json()
    accion = data.get("accion")
    origen = data.get("origen", "app")
    if not accion:
        raise HTTPException(400, "Acción requerida")
    
    cmd = HardwareCommand(accion=accion, origen=origen)
    if "payload" in data:
        cmd.payload = data["payload"]

    db.add(cmd)
    db.commit()
    db.refresh(cmd)

    # --- INTEGRACION DIRECTA RawBT (ANDROID EDGE) ---
    # Si la TPV está corriendo en la misma tablet (Termux), puede acceder a RawBT en 127.0.0.1:40213
    # Generamos código ESC/POS simple para enviar
    try:
        rawbt_url = "http://127.0.0.1:40213/"
        esc_pos_data = b""
        
        if accion == "abrir_caja":
            # ESC p m t1 t2 (Abrir cajón)
            esc_pos_data = b"\x1B\x70\x00\x19\xFA"
            
        elif accion == "imprimir" and "payload" in data:
            import json
            p_data = json.loads(data["payload"])
            t = f"\n--- CARBONES Y POLLOS ---\n"
            t += f"Ticket: {p_data.get('numero_ticket')}\n"
            t += f"Tipo: {p_data.get('tipo', 'cliente').upper()}\n"
            t += "-------------------------\n"
            for it in p_data.get("items", []):
                t += f"{it.get('cantidad')}x {it.get('nombre')}  {it.get('precio', 0.0):.2f}E\n"
            t += "-------------------------\n"
            t += f"TOTAL: {p_data.get('total', 0.0):.2f} E\n"
            t += "-------------------------\n\n\n\n\n"
            # Añadir corte parcial ESC m
            esc_pos_data = t.encode("utf-8") + b"\x1B\x6D"

        if esc_pos_data:
            import urllib.request
            req = urllib.request.Request(rawbt_url, data=esc_pos_data, method='POST')
            urllib.request.urlopen(req, timeout=1.5)
            print("=> RawBT Print EXITOSO")
    except Exception as e:
        # Falla silenciosamente (ej. si este código está ejecutándose en la nube VPS)
        # El polling agent de Windows (si se usara) recogería el comando de BD de todos modos.
        print(f"Nota: RawBT local no disponible ({e})")
    
    return {"status": "ok", "msj": f"Comando {accion} procesado", "id": cmd.id}

@app.get("/api/hardware/poll")
def hw_poll(db: Session = Depends(get_db)):
    """(Edge) La tablet de la tienda pregunta si hay acciones pendientes."""
    cmds = db.query(HardwareCommand).filter(HardwareCommand.estado == "PENDIENTE").all()
    out = []
    import json
    for c in cmds:
        p_json = None
        if c.payload:
            try:
                p_json = json.loads(c.payload)
            except:
                pass
        out.append({"id": c.id, "accion": c.accion, "origen": c.origen, "payload": p_json})
    return {"status": "ok", "comandos": out}

@app.post("/api/hardware/ack/{cmd_id}")
def hw_ack(cmd_id: str, db: Session = Depends(get_db)):
    """(Edge) La tablet confirma que ejecutó la acción."""
    cmd = db.query(HardwareCommand).filter(HardwareCommand.id == cmd_id).first()
    if cmd:
        cmd.estado = "EJECUTADO"
        from datetime import datetime
        cmd.fecha_ejecucion = datetime.now()
        db.commit()
        return {"status": "ok"}
    raise HTTPException(404, "Comando no encontrado")

# --- INTEGRACIÓN WHATSAPP AI (WAHA) ---
from ai_agent import procesar_mensaje_whatsapp

@app.post("/webhook/waha")
async def waha_webhook(request: Request, db: Session = Depends(get_db)):
    """(Cloud) Recibe todos los mensajes entrantes de WhatsApp desde WAHA."""
    try:
        data = await request.json()
        logging.info(f"Webhook WAHA recibido: {json.dumps(data)}")
        
        # Parsear evento de WAHA
        if data.get("event") == "message":
            payload = data.get("payload", {})
            from_number = payload.get("from")
            text_body = payload.get("body", "")
            from_me = payload.get("fromMe", False)
            
            # Solo procesamos si no lo hemos enviado nosotros (evitar bucles) y si es un mensaje de texto
            if not from_me and text_body:
                # Llamar al cerebro AI
                respuesta = procesar_mensaje_whatsapp(text_body, from_number, db)
                if respuesta:
                    # Enviar respuesta de vuelta vía WAHA
                    waha_url = os.environ.get("WAHA_URL", "http://113.30.148.104:3000")
                    session_name = os.environ.get("WAHA_SESSION", "carbones")
                    api_key = os.environ.get("WAHA_HTTP_API_KEY", "1060705b0a574d1fbc92fa10a2b5aca7")
                    
                    headers = {"Content-Type": "application/json"}
                    if api_key:
                        headers["X-Api-Key"] = api_key
                        
                    payload_envio = {
                        "chatId": from_number,
                        "text": respuesta,
                        "session": session_name
                    }
                    try:
                        requests.post(f"{waha_url}/api/sendText", json=payload_envio, headers=headers, timeout=5)
                    except Exception as e:
                        logging.error(f"Error enviando mensaje por WAHA: {e}")
                        
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error en webhook WAHA: {e}")
        return {"status": "error", "message": str(e)}

# --- PASARELA DE PAGOS (STRIPE) ---
import stripe

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    try:
        # Si no hay secret configurado (ej en local), podemos procesarlo sin firma
        if not endpoint_secret:
            event = json.loads(payload)
        else:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
    except Exception as e:
        logging.error(f"Error parseando webhook Stripe: {e}")
        raise HTTPException(status_code=400, detail="Error en firma o payload")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        pedido_id_str = session.get('metadata', {}).get('pedido_id')
        if pedido_id_str:
            pedido_id = pedido_id_str
            pedido = db.query(Pedido).get(pedido_id)
            if pedido:
                pedido.estado = "PAGADO"
                # TODO: Enviar mensaje WAHA confirmando el pago al cliente y al restaurante
                db.commit()
                logging.info(f"Pedido {pedido_id} marcado como PAGADO vía Stripe.")

    return {"status": "success"}

from fastapi.responses import HTMLResponse

@app.get("/pago_completado", response_class=HTMLResponse)
def pago_completado(session_id: str = ""):
    return """
    <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Pago Completado</title></head>
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#f0fdf4; color:#166534;">
            <h1 style="font-size:3rem;">✅ ¡Pago Exitoso!</h1>
            <p style="font-size:1.2rem;">Tu pedido ha sido pagado correctamente y estamos preparándolo.</p>
            <p>¡Gracias por confiar en Carbones y Pollos!</p>
        </body>
    </html>
    """

@app.get("/pago_cancelado", response_class=HTMLResponse)
def pago_cancelado():
    return """
    <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Pago Cancelado</title></head>
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#fef2f2; color:#991b1b;">
            <h1 style="font-size:3rem;">❌ Pago Cancelado</h1>
            <p style="font-size:1.2rem;">Has cancelado el proceso de pago. Tu pedido sigue pendiente.</p>
            <p>Si has tenido algún problema, contáctanos por WhatsApp.</p>
        </body>
    </html>
    """

# --- PEDIDOS A PROVEEDORES ---
class PedidoProveedorReq(BaseModel):
    producto: str
    cantidad: float
    telefono_proveedor: str

@app.post("/api/proveedores/pedir")
def pedir_proveedor(req: PedidoProveedorReq):
    waha_url = os.environ.get("WAHA_URL", "http://113.30.148.104:3000")
    session_name = os.environ.get("WAHA_SESSION", "carbones")
    api_key = os.environ.get("WAHA_HTTP_API_KEY", "1060705b0a574d1fbc92fa10a2b5aca7")
    
    # Formatear mensaje
    mensaje = f"👋 Hola, somos Carbones y Pollos.\n"
    mensaje += f"Necesitamos hacer un pedido de *{req.cantidad}* de *{req.producto}* para lo antes posible.\n"
    mensaje += "Por favor, confirmad recepción del pedido. ¡Gracias!"
    
    payload_envio = {
        "chatId": f"{req.telefono_proveedor}@c.us",
        "text": mensaje,
        "session": session_name
    }
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key
        
    try:
        r = requests.post(f"{waha_url}/api/sendText", json=payload_envio, headers=headers, timeout=5)
        r.raise_for_status()
        return {"status": "ok", "msj": "Pedido enviado al proveedor por WhatsApp"}
    except Exception as e:
        raise HTTPException(500, f"Error contactando al proveedor: {e}")

class CierreZReq(BaseModel):
    efectivo_declarado: float = None

@app.post("/api/admin/trigger_cierre_z")
def trigger_cierre_z_manual(req: CierreZReq = None, db: Session = Depends(get_db)):
    """Endpoint manual para forzar el Cierre Z (Ideal para pruebas o cierres anticipados, soporta Arqueo Ciego)"""
    try:
        import reporte_z
        ef_decl = req.efectivo_declarado if req else None
        msg = reporte_z.generar_reporte_z(efectivo_declarado=ef_decl)
        reporte_z.enviar_whatsapp(msg)
        return {"status": "ok", "msj": "Cierre Z forzado ejecutado con éxito. WhatsApp enviado y mermas procesadas."}
    except Exception as e:
        raise HTTPException(500, f"Error forzando Cierre Z: {str(e)}")

# --- AUTOMATIZACIÓN NOCTURNA (Cron) ---
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

def job_cierre_z():
    import reporte_z
    try:
        msg = reporte_z.generar_reporte_z()
        reporte_z.enviar_whatsapp(msg)
        logging.info("Cierre Z automático ejecutado con éxito.")
    except Exception as e:
        logging.error(f"Error en Cierre Z automático: {e}")

def job_mantenimiento():
    import db_maintenance
    try:
        db_maintenance.run_maintenance()
        logging.info("Mantenimiento semanal automático ejecutado con éxito.")
    except Exception as e:
        logging.error(f"Error en Mantenimiento automático: {e}")

# Instanciamos el planificador horario Europa/Madrid
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Madrid'))
scheduler.add_job(job_cierre_z, 'cron', hour=23, minute=59)
scheduler.add_job(job_mantenimiento, 'cron', day_of_week='sun', hour=3, minute=0)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    logging.info("Cron interno iniciado: Cierre Z (23:59) y Mantenimiento BD (Dom 03:00)")

@app.get("/api/reportes/historico")
def obtener_historico_cierres():
    db: Session = SessionLocal()
    try:
        # Obtenemos los últimos 14 cierres, ordenados por fecha descendente
        cierres = db.query(ReporteZ).order_by(ReporteZ.fecha_cierre.desc()).limit(14).all()
        resultado = []
        for c in cierres:
            resultado.append({
                "id": c.id,
                "fecha": c.fecha_cierre.strftime("%Y-%m-%d %H:%M:%S"),
                "total_caja": round(c.total_caja, 2),
                "pollos_vendidos": c.pollos_vendidos,
                "coste_mermas": round(c.coste_mermas, 2),
                "resumen": c.resumen_texto
            })
        return resultado
    finally:
        db.close()

# --- API B2C (CLIENTES MÓVILES) ---
from pydantic import BaseModel
import stripe_service

class B2CAuthRequest(BaseModel):
    telefono: str
    nombre: str = None

@app.post("/api/b2c/auth")
def b2c_auth(req: B2CAuthRequest, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.telefono == req.telefono).first()
    if not cliente:
        cliente = Cliente(telefono=req.telefono, nombre=req.nombre)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return {"status": "ok", "cliente_id": cliente.id, "nombre": cliente.nombre, "nivel": cliente.nivel_fidelidad, "puntos": cliente.puntos_fidelidad}

@app.get("/api/b2c/me/{cliente_id}")
def b2c_me(cliente_id: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    
    pedidos = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).order_by(Pedido.fecha.desc()).limit(5).all()
    historial = []
    for p in pedidos:
        historial.append({
            "id": p.id,
            "numero_ticket": p.numero_ticket,
            "fecha": p.fecha.strftime("%d/%m/%Y"),
            "total": p.total,
            "estado": p.estado
        })
        
    return {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "telefono": cliente.telefono,
        "nivel": cliente.nivel_fidelidad,
        "puntos": cliente.puntos_fidelidad,
        "historial": historial
    }

@app.post("/api/b2c/checkout/{pedido_id}")
def b2c_checkout(pedido_id: str, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    if pedido.estado != "ESPERANDO_PAGO":
        raise HTTPException(400, "El pedido no está pendiente de pago")

    # Generar resumen de items
    nombres_items = []
    for it in pedido.items:
        prod = db.query(Producto).get(it.producto_id)
        if prod:
            nombres_items.append(f"{it.cantidad}x {prod.nombre}")
    resumen = ", ".join(nombres_items)

    url = stripe_service.generar_enlace_pago(pedido.id, pedido.total, resumen)
    if not url:
        raise HTTPException(500, "Error generando enlace de Stripe")
        
    return {"url": url}

@app.get("/api/b2c/webhook_success")
def b2c_pago_exitoso(session_id: str, db: Session = Depends(get_db)):
    import stripe
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        pedido_id_str = session.metadata.get('pedido_id')
        if not pedido_id_str:
            return HTMLResponse("<h1>Error: Pedido no encontrado en la sesión de Stripe</h1>")
            
        pedido_id = pedido_id_str
        pedido = db.query(Pedido).get(pedido_id)
        
        if pedido and pedido.estado == "ESPERANDO_PAGO":
            pedido.estado = "EN_PREPARACION"
            pedido.metodo_pago = "TARJETA (ONLINE)"
            pedido.stripe_session_id = session_id
            
            # Encolar tickets
            items = []
            for db_it in pedido.items:
                prod = db.query(Producto).get(db_it.producto_id)
                items.append({"nombre": prod.nombre if prod else "Desconocido", "cantidad": db_it.cantidad, "precio": db_it.precio_unitario * db_it.cantidad})
                
            payload = {
                "numero_ticket": pedido.numero_ticket,
                "origen": pedido.origen,
                "total": pedido.total,
                "items": items,
                "base_imponible_10": pedido.base_imponible_10,
                "cuota_iva_10": pedido.cuota_iva_10,
                "base_imponible_21": pedido.base_imponible_21,
                "cuota_iva_21": pedido.cuota_iva_21,
                "notas_cliente": pedido.notas_cliente
            }
            
            import json
            # No abrimos caja porque es pago online
            # Imprimir cocina
            payload["tipo"] = "cocina"
            db.add(HardwareCommand(accion="imprimir", origen="b2c_online", payload=json.dumps(payload)))
            # Imprimir cliente
            payload["tipo"] = "cliente"
            db.add(HardwareCommand(accion="imprimir", origen="b2c_online", payload=json.dumps(payload)))
            
            db.commit()
            
        return HTMLResponse(f"<h1>¡Pago Completado!</h1><p>Tu pedido {pedido.numero_ticket if pedido else ''} ya se está preparando en cocina.</p><br><a href='/'>Volver al inicio</a>")
    except Exception as e:
        return HTMLResponse(f"<h1>Error validando el pago: {e}</h1>")


@app.post("/api/b2c/reviews")
def crear_review(review_data: ReviewCrear, db: Session = Depends(get_db)):
    from models import Review
    nueva_review = Review(
        pedido_id=review_data.pedido_id,
        cliente_id=review_data.cliente_id,
        rating=review_data.rating,
        comentario=review_data.comentario
    )
    db.add(nueva_review)
    db.commit()
    return {"status": "ok", "msj": "Review guardada"}

@app.get("/api/b2c/dashboard_stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from models import Pedido, MovimientoStock, Review, ItemPedido, Producto, Cliente
    import datetime
    
    hoy = datetime.date.today()
    pedidos_hoy = db.query(Pedido).filter(Pedido.fecha >= hoy).all()
    
    ventas_hoy = sum(p.total for p in pedidos_hoy if p.estado == "LISTO" or p.estado == "EN_PREPARACION")
    pedidos_b2c = sum(1 for p in pedidos_hoy if p.origen == "B2C_MOBILE")
    
    mermas_hoy = db.query(MovimientoStock).filter(MovimientoStock.fecha >= hoy, MovimientoStock.tipo == "MERMA").all()
    # Aproximación de coste de mermas: buscar el precio del producto y descontar un 30% como coste
    coste_mermas = 0
    for m in mermas_hoy:
        prod = db.query(Producto).get(m.producto_id)
        if prod:
            coste_mermas += abs(m.cantidad) * (prod.precio * 0.3)
            
    reviews = db.query(Review).order_by(Review.fecha.desc()).limit(20).all()
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
    # Gráficos
    horas = [0]*24
    for p in pedidos_hoy:
        if p.estado in ["LISTO", "EN_PREPARACION"]:
            horas[p.fecha.hour] += p.total
            
    # Reducir horas para el gráfico a las horas de apertura típicas (ej. 10 a 22)
    labels_horas = [f"{i}:00" for i in range(10, 23)]
    data_horas = [horas[i] for i in range(10, 23)]
    
    # Top Productos
    prod_counts = {}
    for p in pedidos_hoy:
        if p.estado in ["LISTO", "EN_PREPARACION"]:
            for it in p.items:
                prod_counts[it.producto_id] = prod_counts.get(it.producto_id, 0) + it.cantidad
                
    pollos_counts = {}
    pizzas_counts = {}
    from models import Categoria
    for pid, count in prod_counts.items():
        prod = db.query(Producto).get(pid)
        if prod and prod.categoria_id:
            cat = db.query(Categoria).get(prod.categoria_id)
            if cat:
                if "Pollo" in cat.nombre:
                    pollos_counts[pid] = count
                elif "Pizza" in cat.nombre:
                    pizzas_counts[pid] = count

    def get_top(counts):
        top_ids = sorted(counts, key=counts.get, reverse=True)[:5]
        labels = []
        data = []
        for pid in top_ids:
            prod = db.query(Producto).get(pid)
            labels.append(prod.nombre if prod else f"Prod #{pid}")
            data.append(counts[pid])
        return {"labels": labels, "data": data}

    # Formatear reviews
    formatted_reviews = []
    for r in reviews:
        cliente_nombre = "Anónimo"
        if r.cliente_id:
            c = db.query(Cliente).get(r.cliente_id)
            if c and c.nombre:
                cliente_nombre = c.nombre
        formatted_reviews.append({
            "cliente_nombre": cliente_nombre,
            "rating": r.rating,
            "comentario": r.comentario,
            "fecha": r.fecha.strftime("%d/%m %H:%M")
        })

    return {
        "kpis": {
            "ventas_hoy": ventas_hoy,
            "coste_mermas": coste_mermas,
            "pedidos_b2c": pedidos_b2c,
            "avg_rating": avg_rating
        },
        "charts": {
            "horas": {
                "labels": labels_horas,
                "data": data_horas
            },
            "pollos": get_top(pollos_counts),
            "pizzas": get_top(pizzas_counts)
        },
        "reviews": formatted_reviews
    }

@app.get("/api/b2c/ia_insights")
def get_ia_insights(db: Session = Depends(get_db)):
    from models import Review, Pedido, Producto, ItemPedido
    import datetime
    
    # Reseñas
    reviews = db.query(Review).order_by(Review.fecha.desc()).limit(10).all()
    avg = sum(r.rating for r in reviews) / len(reviews) if reviews else 5.0
    
    # Análisis de Alérgenos y Complementos de HOY
    hoy = datetime.date.today()
    pedidos_hoy = db.query(Pedido).filter(Pedido.fecha >= hoy).all()
    
    alergenos_detectados = set()
    complementos_vendidos = 0
    
    for p in pedidos_hoy:
        for it in p.items:
            prod = db.query(Producto).get(it.producto_id)
            if prod:
                if prod.alergenos:
                    for al in prod.alergenos.split(","):
                        alergenos_detectados.add(al.strip().lower())
                if prod.is_addon:
                    complementos_vendidos += it.cantidad
                    
    try:
        import google.generativeai as genai
        import json
        
        # Asume que genai.configure() ya ha cargado la key globalmente o usa .env
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "YOUR_GEMINI_KEY"))
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        
        prompt = f"""
        Eres el analista de datos y chef experto del restaurante 'Carbones y Pollos'.
        Tienes los siguientes datos del turno actual:
        - Valoración media de los clientes recientes: {avg:.1f}/5.0
        - Alérgenos requeridos en los pedidos de hoy: {', '.join(alergenos_detectados) if alergenos_detectados else 'Ninguno detectado'}
        - Complementos extra vendidos hoy: {complementos_vendidos}
        
        Basándote en estos datos, genera un análisis corto en formato JSON con exactamente estas dos claves:
        - "resumen_reviews": Un resumen analítico corto de cómo perciben los clientes el servicio (basado en el {avg:.1f}/5.0).
        - "sugerencia_produccion": Una recomendación directa y profesional a los cocineros en base a los alérgenos, el volumen de complementos y las ventas actuales. Sé específico y motivador.

        Devuelve SOLO código JSON válido, sin formato Markdown alrededor (sin ```json), listo para ser parseado por json.loads().
        """
        
        response = model.generate_content(prompt)
        ai_data = json.loads(response.text.strip())
        
        return {
            "resumen_reviews": ai_data.get("resumen_reviews", "Análisis no disponible."),
            "sugerencia_produccion": ai_data.get("sugerencia_produccion", "Continúa el servicio con normalidad.")
        }
        
    except Exception as e:
        # Fallback en caso de error de API o Parsing
        return {
            "resumen_reviews": f"Error conectando con Gemini: {str(e)[:50]}",
            "sugerencia_produccion": "Servicio de IA temporalmente inactivo. Sigue los protocolos manuales."
        }

# Montar frontend estático OBLIGATORIAMENTE al final
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001)
