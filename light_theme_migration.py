import os
import re

files_to_update = [
    'static/dashboard.html',
    'static/rrhh.html',
    'static/liquidaciones.html',
    'static/caja.html',
    'static/kds.html',
    'static/inventario.html',
    'static/stats.html',
    'static/repartidores.html'
]

replacements = [
    (r'--bg-base:\s*#020617;', '--bg-base: #f8fafc;'),
    (r'--glass-bg:\s*rgba\(15,\s*23,\s*42,\s*0\.6\);', '--glass-bg: rgba(255, 255, 255, 0.8);'),
    (r'--glass-border:\s*rgba\(255,\s*255,\s*255,\s*0\.08\);', '--glass-border: rgba(0, 0, 0, 0.05);'),
    (r'text-slate-300', 'text-slate-600'),
    (r'text-white', 'text-slate-900'),
    (r'bg-slate-800/80', 'bg-white shadow-sm border border-slate-100'),
    (r'bg-slate-900/50', 'bg-slate-50 border border-slate-100'),
    (r'bg-slate-900', 'bg-white'),
    (r'bg-slate-800', 'bg-white'),
    (r'border-slate-700', 'border-slate-200'),
    (r'border-white/5', 'border-slate-100'),
    (r'border-white/10', 'border-slate-200'),
    (r'text-slate-400', 'text-slate-500'),
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in replacements:
            content = re.sub(old, new, content)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"File not found {filepath}")
