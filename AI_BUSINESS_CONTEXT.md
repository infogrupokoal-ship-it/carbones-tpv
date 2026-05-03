# AI BUSINESS CONTEXT

## Identidad del Negocio
- **Razón Social:** Carbones y Pollos La Granja S.L.
- **NIF:** B24823270
- **Ubicación:** Av. Malvarrosa 112, Bajo, 46011 Valencia.
- **Teléfono de Pedidos:** 654 445 516
- **Sector:** Comida para llevar (Delivery & Takeaway). No tiene servicio de mesa.

## Oferta Gastronómica Principal
- Pollos asados, brasas, arroces, raciones, menús combinados.
- Carta Nocturna / Fines de Semana: Bocadillos, chivitos, brascadas, hamburguesas.

## Flujos Operativos Reales

### 1. El Mostrador (Punto de Venta Central / Cajero)
Alta afluencia. Se requiere cobrar rápido.
- Entra el cliente, se le toma nota rápida.
- El sistema debe añadir al carrito y cobrar en 2 clicks.
- Imprime ticket para el cliente (Impresora 58mm Mostrador).
- Si requiere preparación en caliente, imprime en Cocina.

### 2. La Cocina (KDS y Producción)
Carga alta de trabajo visual y térmica.
- Pantalla (KDS) en tablet/monitor o tira de papel continuo (UROVO 80mm).
- Se necesita dividir platos fríos (ya hechos) de calientes (a hacer).
- Sistema de control de estado: Recibido -> Preparando -> Listo.

### 3. Caja / Cuadratura Diaria
- Turnos muy marcados (Mañanas para pollos/arroces, Noches para bocadillos).
- Arqueo de caja y "Reporte Z" físico al final del turno.

### 4. Canal de WhatsApp
- Se espera alta recepción de pedidos por mensaje de texto.
- La IA (Gemini) actuará de orquestador leyendo la carta y cotizando el pedido al cliente antes de inyectarlo en el KDS de la tienda.

## Extracto de la Carta Nocturna (Data Real)

**BOCADILLOS Y CHIVITOS**
- Chivito de pollo: 6,50 € (Mayonesa, tomate, cebolla, lechuga, pechuga, queso, bacon)
- Chivito de ternera: 7,00 €
- Chivito de carne de caballo: 8,00 €
- Lomo, queso y bacon: 6,50 €
- Hamburguesa completa: 5,50 €

**BRASCADAS**
- Brascada normal: 6,50 €
- Brascada de caballo: 7,00 €

**ESPECIALES**
- Cabramelizado La Granja: 7,50 € (Cebolla caramelizada, queso cabra, pollo, bacon, jamón)
- Calamares con alioli: 8,00 €
- Chistorra, patatas, huevos fritos: 5,50 €

## Estructura de Datos Recomendada para los Productos
- `nombre` y `descripcion`
- `precio`
- `turno`: `MORNING` (Pollos), `NIGHT` (Bocadillos), `ALL`.
- `disponible_tpv` (Bool).
- `disponible_whatsapp` (Bool).
- `requiere_cocina` (Si es false, se da directamente en mostrador, no imprime ticket UROVO).
- `impresora_destino` (Frio/Caliente).
- `modificadores`: (Sin queso, +Bacon, etc).
