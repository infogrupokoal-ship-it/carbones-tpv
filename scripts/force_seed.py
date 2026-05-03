import os
import sys

# Añadir el directorio raíz al path para poder importar backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
from backend.models import *
from scripts.seed_ultra import seed_ultra_industrial

def force_reset_and_seed():
    print("🔥 INICIANDO RESET INDUSTRIAL DE BASE DE DATOS...")
    
    # 1. Eliminar todas las tablas
    print("🗑️ Eliminando tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. Recrear tablas
    print("🏗️ Recreando esquema de base de datos...")
    Base.metadata.create_all(bind=engine)
    
    # 3. Ejecutar Seeding
    print("🧫 Ejecutando Seeding Ultra Industrial...")
    seed_ultra_industrial()
    
    print("\n✅ PROCESO COMPLETADO CON ÉXITO.")
    print("   - Tablas recreadas.")
    print("   - Catálogo industrial cargado.")
    print("   - Usuarios administrativos creados (admin:1234).")

if __name__ == "__main__":
    confirm = input("⚠️ ADVERTENCIA: Esto borrará TODOS los datos. ¿Continuar? (s/n): ")
    if confirm.lower() == 's':
        force_reset_and_seed()
    else:
        print("Operación cancelada.")
