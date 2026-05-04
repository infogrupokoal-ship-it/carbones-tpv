# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Producto  # ajusta nombre real si difiere

CARTA_NOCTURNA = [
    {"slug":"chivito-pollo","nombre":"Chivito de pollo","precio_base":8.9},
    {"slug":"chivito-lomo","nombre":"Chivito de lomo","precio_base":8.9},
    {"slug":"chivito-ternera","nombre":"Chivito de ternera","precio_base":9.5},
    {"slug":"chivito-caballo","nombre":"Chivito de carne de caballo","precio_base":9.8},
    {"slug":"lomo-queso-bacon","nombre":"Lomo, queso y bacon","precio_base":7.9},
    {"slug":"bocadillo-hamburguesa-completa","nombre":"Bocadillo de hamburguesa completa","precio_base":8.5},
    {"slug":"bocadillo-al-gusto","nombre":"Bocadillo al gusto","precio_base":0.0,"precio_manual_permitido":True},
    {"slug":"brascada","nombre":"Brascada","precio_base":8.2},
    {"slug":"brascada-lomo","nombre":"Brascada de lomo","precio_base":8.4},
    {"slug":"brascada-caballo","nombre":"Brascada de caballo","precio_base":8.9},
    {"slug":"cabramelizado-la-granja","nombre":"Bocadillo Cabramelizado La Granja","precio_base":9.2},
    {"slug":"sobrasada-lomo-queso-bacon","nombre":"Sobrasada, lomo, queso y bacon","precio_base":8.3},
    {"slug":"lomo-pimientos-cebolla","nombre":"Lomo, pimientos, cebolla a la plancha","precio_base":8.1},
    {"slug":"sepia-mayonesa","nombre":"Bocadillo de sepia a la plancha con mayonesa","precio_base":9.4},
    {"slug":"calamares-alioli","nombre":"Calamares con alioli","precio_base":8.9},
    {"slug":"revuelto-gambas-ajos-tiernos","nombre":"Revuelto de gambas con ajos tiernos","precio_base":9.7},
    {"slug":"tomate-anchoas-queso","nombre":"Tomate, anchoas y queso","precio_base":7.8},
    {"slug":"bocadillo-vegetal","nombre":"Bocadillo vegetal","precio_base":7.2},
    {"slug":"tortilla-patatas-alioli","nombre":"Tortilla de patatas con alioli","precio_base":7.4},
    {"slug":"tortilla-francesa-tomate-longanizas","nombre":"Tortilla francesa, tomate y longanizas","precio_base":7.9},
    {"slug":"embutidos-pisto","nombre":"Embutidos con pisto","precio_base":8.0},
    {"slug":"pechuga-empanada","nombre":"Pechuga empanada","precio_base":7.6},
    {"slug":"huevos-chistorra-patatas-alioli","nombre":"Huevos fritos, chistorra, patatas y alioli","precio_base":8.6},
]

def upsert_carta_nocturna(db: Session):
    for p in CARTA_NOCTURNA:
        obj = db.query(Producto).filter(Producto.nombre == p["nombre"]).first()
        payload = {
            "nombre": p["nombre"],
            "descripcion": p["nombre"],
            "precio": p["precio_base"],
            "precio_base": p["precio_base"],
            "turno_disponible": "noche",
            "is_active": True,
            "alergenos": "Pendiente validación humana",
        }
        if obj:
            for k, v in payload.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
        else:
            db.add(Producto(**{k:v for k,v in payload.items() if hasattr(Producto, k)}))
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        upsert_carta_nocturna(db)
        print("OK: carta nocturna insert/update completada.")
    finally:
        db.close()
