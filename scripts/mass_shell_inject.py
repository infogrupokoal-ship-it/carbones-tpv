import os

HTML_DIR = "static"
SHELL_DIV = '<div id="enterprise-sidebar"></div>'
SHELL_JS = '<script src="/static/js/enterprise_shell.js"></script>'

# Updated mapping of filename to module ID (Comprehensive)
MODULE_MAP = {
    "portal.html": "Portal",
    "stats.html": "Analytics",
    "analytics.html": "Analytics",
    "inventario.html": "Stock",
    "dashboard_produccion.html": "Producción",
    "caja.html": "Caja",
    "kds.html": "KDS",
    "rrhh.html": "RRHH",
    "marketing.html": "Marketing",
    "reparto.html": "Reparto",
    "referidos.html": "Referidos",
    "escandallos.html": "Escandallos",
    "auditoria.html": "Auditoría",
    "settings.html": "Ajustes",
    "iot.html": "IoT Equipos",
    "franchise.html": "Franquicias",
    "esg.html": "ESG & Eco",
    "menu_engineering.html": "Menu Eng.",
    "fleet_map.html": "Fleet",
    "erp.html": "ERP",
    "commercial.html": "B2B Sales",
    "loyalty.html": "Loyalty",
    "hardware.html": "Hardware",
    "mantenimiento.html": "Maintenance",
    "crisis.html": "Crisis",
    "procurement.html": "Procurement",
    "delivery_aggregators.html": "Aggregators"
}

def inject_shell():
    print("Starting Mass Shell Injection v3.1...")
    for filename, module_id in MODULE_MAP.items():
        path = os.path.join(HTML_DIR, filename)
        if not os.path.exists(path):
            print(f"Skip: {filename} not found.")
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ensure data-active-module is in body
        if f'data-active-module="' not in content:
            content = content.replace("<body", f'<body data-active-module="{module_id}"')
        else:
            # Update existing module id
            import re
            content = re.sub(r'data-active-module="[^"]*"', f'data-active-module="{module_id}"', content)
            
        # Ensure sidebar div is there
        if SHELL_DIV not in content:
            if "<body>" in content:
                content = content.replace("<body>", f"<body>\n    {SHELL_DIV}")
            else:
                # Handle cases with classes in body
                content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + f"\n    {SHELL_DIV}", content)
        
        # Ensure script is there
        if SHELL_JS not in content:
            if "</body>" in content:
                content = content.replace("</body>", f"    {SHELL_JS}\n</body>")
            else:
                content += f"\n{SHELL_JS}"
            
        # Ensure enterprise_shell.css is there
        if "enterprise_shell.css" not in content:
            content = content.replace("</head>", '    <link rel="stylesheet" href="/static/css/enterprise_shell.css">\n</head>')

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Injected: {filename}")

if __name__ == "__main__":
    inject_shell()
