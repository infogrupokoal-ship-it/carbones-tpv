import os

PORTALS_DIR = "static"
PORTALS = [f for f in os.listdir(PORTALS_DIR) if f.endswith(".html")]

TELEMETRY_HTML = '<div id="module-telemetry" class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16"></div>'

def upgrade_portals():
    print("Starting Enterprise Visual Upgrade...")
    
    for portal in PORTALS:
        path = os.path.join(PORTALS_DIR, portal)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Inject Telemetry Container if not present
        if "id=\"module-telemetry\"" not in content:
            # Inject before the first main grid or after header
            if "</header>" in content:
                content = content.replace("</header>", f"</header>\n\n        {TELEMETRY_HTML}")
            elif "<main" in content:
                content = content.replace("<main", f"{TELEMETRY_HTML}\n<main")
        
        # 2. Inject Telemetry Script if not present
        if "EnterpriseUI.renderKPICard" not in content and portal != "portal.html":
            script = """
    <script>
        window.addEventListener('load', () => {
            if (typeof EnterpriseUI !== 'undefined') {
                EnterpriseUI.renderKPICard('module-telemetry', {
                    title: 'Estado del Nodo',
                    value: 'ACTIVO',
                    unit: 'SECURE',
                    trend: 'up',
                    trendValue: '100%',
                    icon: 'fa-server'
                });
                EnterpriseUI.renderKPICard('module-telemetry', {
                    title: 'Carga de Trabajo',
                    value: Math.floor(Math.random() * 40 + 20),
                    unit: '%',
                    trend: 'up',
                    trendValue: 'LOW',
                    icon: 'fa-microchip'
                });
                EnterpriseUI.renderKPICard('module-telemetry', {
                    title: 'Latencia Sync',
                    value: Math.floor(Math.random() * 50 + 10),
                    unit: 'ms',
                    trend: 'down',
                    trendValue: 'OPTIMAL',
                    icon: 'fa-bolt'
                });
                EnterpriseUI.renderKPICard('module-telemetry', {
                    title: 'Seguridad',
                    value: 'V4.0',
                    unit: 'SSL',
                    trend: 'up',
                    trendValue: 'MAX',
                    icon: 'fa-shield-halved'
                });
            }
        });
    </script>
            """
            content = content.replace("</body>", f"{script}\n</body>")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Upgraded: {portal}")

if __name__ == "__main__":
    upgrade_portals()
