import re

with open('static/kiosko.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace variable declarations
content = content.replace("let userRole = 'quiosko';", "let tpvDeviceMode = 'b2c';")
content = content.replace("let userName = 'Cliente';", "let tpvB2cTipo = 'ahora';")

# 2. Replace checkRole function
old_checkRole = """        function checkRole() {
            userRole = localStorage.getItem('tpv_role');
            userName = localStorage.getItem('tpv_name');
            
            if (!userRole) {
                window.location.href = 'index.html';
                return;
            }
            
            if (userRole === 'responsable') {
                document.getElementById('admin-buttons').classList.remove('hidden');
                document.getElementById('admin-buttons').classList.add('flex');
            } else {
                document.getElementById('admin-buttons').classList.add('hidden');
                document.getElementById('admin-buttons').classList.remove('flex');
            }
        }"""

new_checkRole = """        function checkRole() {
            tpvDeviceMode = localStorage.getItem('tpv_device_mode');
            tpvB2cTipo = localStorage.getItem('tpv_b2c_tipo') || 'ahora';
            
            if (!tpvDeviceMode) {
                tpvDeviceMode = 'b2c';
                localStorage.setItem('tpv_device_mode', 'b2c');
            }
            
            if (tpvDeviceMode === 'admin' || tpvDeviceMode === 'caja') {
                document.getElementById('admin-buttons')?.classList.remove('hidden');
                document.getElementById('admin-buttons')?.classList.add('flex');
            } else {
                document.getElementById('admin-buttons')?.classList.add('hidden');
                document.getElementById('admin-buttons')?.classList.remove('flex');
            }
            
            if (tpvDeviceMode !== 'b2c') {
                const revBtn = document.getElementById('btn-review-flotante');
                if(revBtn) revBtn.classList.add('hidden');
            }
        }"""
content = content.replace(old_checkRole, new_checkRole)

# 3. Replace isB2C line 445
content = content.replace('const isB2C = localStorage.getItem("tpv_role") === "cliente_b2c";', 'const isB2C = tpvDeviceMode === "b2c";')

# 4. Replace other userRole checks
content = content.replace("userRole === 'responsable'", "tpvDeviceMode === 'caja'")
content = content.replace("userRole !== 'quiosko'", "tpvDeviceMode !== 'kiosko_fisico'")
content = content.replace('localStorage.getItem("tpv_role") === "cliente_b2c"', 'localStorage.getItem("tpv_device_mode") === "b2c"')

with open('static/kiosko.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Reemplazos realizados en kiosko.html.")
