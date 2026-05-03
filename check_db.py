import sqlite3
c = sqlite3.connect('instance/tpv_data.sqlite')
cur = c.cursor()
try:
    cur.execute("select nombre, count(*) from productos group by nombre having count(*)>1")
    print('DUPLICATES:', cur.fetchall())
except Exception as e:
    print('DUPLICATES ERROR:', e)

names = ['Chivito de pollo','Chivito de lomo','Chivito de ternera','Chivito de carne de caballo','Lomo, queso y bacon','Bocadillo de hamburguesa completa','Brascada','Brascada de lomo','Brascada de caballo','Bocadillo Cabramelizado La Granja','Sobrasada, lomo, queso y bacon','Lomo, pimientos, cebolla a la plancha','Bocadillo de sepia a la plancha con mayonesa','Calamares con alioli','Revuelto de gambas con ajos tiernos','Tomate, anchoas y queso','Bocadillo vegetal','Tortilla de patatas con alioli','Tortilla francesa, tomate y longanizas','Embutidos con pisto','Pechuga empanada','Huevos fritos, chistorra, patatas y alioli']
missing = []
for n in names:
    try:
        if not cur.execute('select nombre, precio_base, turno, activo from productos where nombre=?', (n,)).fetchone():
            missing.append(n)
    except Exception as e:
        # handle missing columns or table
        try:
            if not cur.execute('select nombre from productos where nombre=?', (n,)).fetchone():
                missing.append(n)
        except Exception:
            missing.append(n)

print('MISSING:', missing)
c.close()
