"""
Seed de precios reales para Carbones y Pollos La Granja
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

PRICES = {
    # Nuestra Brasa
    'Pollo Asado Tradición': 12.90,
    'Costillas a la Brasa': 14.50,
    # Guarniciones
    'Patatas Fritas Caseras': 4.20,
    # Ensaladas
    'Ensalada Mediterránea': 5.90,
    # Bebidas
    'Refresco 33cl': 1.80,
    # Bocadillos y Chivitos
    'CHIVITO DE POLLO': 7.50,
    'CHIVITO DE LOMO': 7.90,
    'CHIVITO DE TERNERA': 8.20,
    'CHIVITO DE CARNE DE CABALLO': 8.50,
    'LOMO, QUESO Y BACON': 7.20,
    'BOCADILLO DE HAMBURGUESA COMPLETA': 6.90,
    'BOCADILLO AL GUSTO': 5.50,
    # Brascadas
    'BRASCADA DE TERNERA': 8.90,
    'BRASCADA DE LOMO': 8.50,
    'BRASCADA DE CABALLO': 9.20,
    # Especiales de la Casa
    'BOCADILLO CABRAMELIZADO LA GRANJA': 9.50,
    'ESPECIAL SOBRASADA': 8.90,
    'LOMO, PIMIENTOS Y CEBOLLA': 8.20,
    'ESPECIAL BLANCO Y NEGRO': 9.80,
    # Del Mar
    'BOCADILLO DE SEPIA A LA PLANCHA': 8.50,
    'CALAMARES A LA ANDALUZA': 7.90,
    'REVUELTO DE GAMBAS': 9.20,
    'ANCHOAS Y QUESO': 8.80,
    # Bocadillos Clásicos
    'BOCADILLO VEGETAL': 6.50,
    'TORTILLA DE PATATAS': 5.90,
    'TORTILLA FRANCESA COMPLETA': 6.20,
    'EMBUTIDOS CON PISTO': 7.50,
    'PECHUGA EMPANADA': 7.90,
    'HUEVOS ROTOS CON CHISTORRA': 8.90,
    # Pizzas
    'PIZZA MARGARITA': 9.90,
    'PIZZA PROSCIUTTO': 11.50,
    'PIZZA CUATRO QUESOS': 12.90,
    'PIZZA BARBACOA': 12.50,
    'PIZZA CARBONARA': 11.90,
    'PIZZA PEPPERONI': 11.50,
    'PIZZA VEGETAL': 10.90,
}

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tpv_data.sqlite')
conn = sqlite3.connect(db_path)
c = conn.cursor()

updated = 0
for nombre, precio in PRICES.items():
    c.execute("UPDATE productos SET precio=? WHERE nombre=?", (precio, nombre))
    if c.rowcount > 0:
        updated += 1
        print(f"  OK: {nombre} -> {precio}EUR")
    else:
        print(f"  NOT FOUND: {nombre}")

conn.commit()
conn.close()
print(f"\nActualizados: {updated}/{len(PRICES)} productos")
