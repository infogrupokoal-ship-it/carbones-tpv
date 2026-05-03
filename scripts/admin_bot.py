# --- Arreglo Proactivo de Codificación en Windows ---
import sys
import io

if sys.platform == "win32":
    try:
        # Forzar UTF-8 en la consola para evitar 'charmap' errors
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

import os
import asyncio
import logging
import time
from datetime import datetime
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv

# Configuración de rutas para importar del backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings
from backend.utils.logger import logger as central_logger
from backend.utils.ai_model_manager import ai_manager, generate_ai_response

# Logger adaptado al central
logger = central_logger

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or settings.TELEGRAM_BOT_TOKEN
TELEGRAM_ADMIN_CHAT_ID = int(os.getenv("TELEGRAM_ADMIN_CHAT_ID") or settings.TELEGRAM_ADMIN_CHAT_ID or 0)

if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN no configurado. El bot no arrancará.")
    sys.exit(1)

async def is_admin(update: Update) -> bool:
    """Verifica si el usuario es el administrador autorizado."""
    user_id = update.effective_user.id
    if user_id == TELEGRAM_ADMIN_CHAT_ID:
        return True
    
    # Si no es admin, informar del Chat ID para configuración
    await update.message.reply_text(
        f"⚠️ **Acceso Denegado**\n"
        f"Tu Chat ID es `{user_id}`.\n"
        f"Añádelo a tu `.env` como `TELEGRAM_ADMIN_CHAT_ID={user_id}`."
    )
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida y Menú Principal."""
    if not await is_admin(update):
        await update.message.reply_text("🚫 Acceso Denegado. Este es un terminal administrativo privado.")
        return

    welcome_msg = (
        "🚀 **Quantum TPV Admin Bot v1.0**\n"
        "Ecosistema: Carbones y Pollos Singularity\n\n"
        "Comandos Disponibles:\n"
        "/status - Estado de salud del TPV\n"
        "/ventas - Resumen de ventas hoy\n"
        "/stock  - Alertas de inventario bajo\n"
        "/health - Telemetría industrial\n"
        "/help   - Ayuda avanzada"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Estado General", callback_data='status')],
        [InlineKeyboardButton("💰 Ventas Hoy", callback_data='ventas')],
        [InlineKeyboardButton("🛠️ Herramientas DevOps", callback_data='devops')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

import httpx
from backend.database import SessionLocal
from backend.models import Pedido, ItemPedido, Producto, Ingrediente

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica la salud del backend local/VPS usando el endpoint de salud."""
    if not await is_admin(update): return

    await update.message.reply_chat_action("find_location")
    
    # Intentar obtener telemetría real
    # Intentamos primero puerto 8000, luego puerto dinámico de Render
    port = os.getenv('PORT', '8000')
    api_url = f"http://localhost:{port}/api/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(api_url)
            data = response.json()
            
            telemetry = data.get("telemetry", {})
            sys_data = telemetry.get("system", {})
            db_data = telemetry.get("database", {})
            
            msg = (
                "🟢 **ESTADO SISTEMA: OPERATIVO**\n"
                f"🏷️ Versión: `{data.get('version')}`\n"
                f"🌍 Entorno: `{data.get('environment')}`\n\n"
                "📊 **TELEMETRÍA**\n"
                f"🧠 CPU: `{sys_data.get('cpu')}`\n"
                f"💾 RAM: `{sys_data.get('memory')}`\n"
                f"🗄️ DB Status: `{db_data.get('status')}` ({db_data.get('latency_ms')}ms)\n"
                f"⏱️ Uptime: `{telemetry.get('uptime_seconds')}s`"
            )
    except Exception as e:
        msg = (
            "🟡 **SISTEMA EN MANTENIMIENTO/OFFLINE**\n"
            f"⚠️ El endpoint `/api/health` no responde en puerto {port}.\n"
            f"🔍 Error: `{str(e)[:100]}`"
        )
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def ventas_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resumen de ventas del día actual."""
    if not await is_admin(update): return
    
    db = SessionLocal()
    try:
        hoy = datetime.now().date()
        ventas = db.query(Pedido).filter(Pedido.fecha >= hoy).all()
        total = sum(v.total for v in ventas)
        count = len(ventas)
        
        msg = (
            f"💰 **VENTAS HOY ({hoy.strftime('%d/%m/%Y')})**\n\n"
            f"📈 Total Ventas: `{total:,.2f}€`\n"
            f"🧾 N° Pedidos: `{count}`\n"
            f"🍱 Ticket Medio: `{ (total/count if count > 0 else 0):,.2f}€`"
        )
    except Exception as e:
        msg = f"❌ Error consultando ventas: {e}"
    finally:
        db.close()
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def stock_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra productos e ingredientes con stock bajo."""
    if not await is_admin(update): return
    
    db = SessionLocal()
    try:
        # Check Productos
        bajo_prod = db.query(Producto).filter(Producto.stock_actual <= Producto.stock_minimo).all()
        # Check Ingredientes
        bajo_ing = db.query(Ingrediente).filter(Ingrediente.stock_actual <= Ingrediente.stock_minimo).all()
        
        if not bajo_prod and not bajo_ing:
            msg = "✅ **STOCK ÓPTIMO**: Todos los ítems están por encima del mínimo."
        else:
            msg = "⚠️ **ALERTA DE STOCK BAJO**\n\n"
            if bajo_prod:
                msg += "*PRODUCTOS (Venta)*\n"
                for item in bajo_prod:
                    msg += f"• {item.nombre}: `{item.stock_actual}` ud (Min: {item.stock_minimo})\n"
                msg += "\n"
            
            if bajo_ing:
                msg += "*INGREDIENTES (Suministros)*\n"
                for item in bajo_ing:
                    msg += f"• {item.nombre}: `{item.stock_actual}` {item.unidad_medida} (Min: {item.stock_minimo})\n"
    except Exception as e:
        msg = f"❌ Error consultando stock: {e}"
    finally:
        db.close()
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa fotos, documentos y audios enviados por el Admin."""
    if not await is_admin(update): return

    await update.message.reply_chat_action("upload_document")
    
    file = None
    original_name = "archivo_bot"
    category = "general"
    
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        original_name = f"photo_{file.file_id}.jpg"
        category = "fotos"
    elif update.message.document:
        file = await update.message.document.get_file()
        original_name = update.message.document.file_name
        category = "documentos"
    
    if not file: return

    try:
        file_bytes = await file.download_as_bytearray()
        
        from backend.multimedia import manager
        db = SessionLocal()
        result = manager.process_file(
            db=db,
            file_content=bytes(file_bytes),
            original_filename=original_name,
            user_id=None,
            category=category
        )
        db.close()
        
        if result.get("ok"):
            msg = (
                f"✅ **ARCHIVO REGISTRADO**\n"
                f"📎 Nombre: `{original_name}`\n"
                f"🏷️ ID: `{result['id']}`\n"
                f"🛡️ MIME: `{result['mime']}`\n"
            )
            
            from backend.utils.ai_model_manager import ai_manager
            prompt = "Analiza este documento/imagen del TPV. Si es un ticket, resume los totales. Si es una incidencia, explícala. Responde breve en Español."
            
            await update.message.reply_chat_action("typing")
            analysis, model = await ai_manager.analyze_multimodal_async(
                prompt=prompt,
                file_bytes=bytes(file_bytes),
                mime_type=result['mime']
            )
            
            if analysis:
                msg += f"\n🤖 **ANÁLISIS IA ({model})**:\n{analysis}"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Error: {result.get('error')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Fallo multimedia: {e}")

async def chat_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja consultas en lenguaje natural usando Gemini con Fallback."""
    if not await is_admin(update): return

    user_query = update.message.text
    await update.message.reply_chat_action("typing")
    
    context_prompt = (
        "Eres el Administrador IA de Carbones y Pollos TPV. "
        "Ayudas al dueño (Jorge) a gestionar el restaurante. "
        "Sé profesional, conciso y técnico cuando sea necesario. "
        "No compartas información sensible como passwords. "
        f"El usuario pregunta: {user_query}"
    )
    
    try:
        # Usar el gestor de modelos con fallback automático
        response_text = await generate_ai_response(context_prompt)
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Error IA: {e}")
        await update.message.reply_text("⚠️ El cerebro IA está experimentando turbulencias. Reintenta en breve.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status_check))
    application.add_handler(CommandHandler('health', status_check))
    application.add_handler(CommandHandler('ventas', ventas_hoy))
    application.add_handler(CommandHandler('stock', stock_alert))
    
    # Manejo de Multimedia (Fotos y Documentos)
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_media))
    
    # Chat General
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_ia))
    
    logger.info("🤖 TPV Admin Bot arrancado correctamente...")
    application.run_polling()
