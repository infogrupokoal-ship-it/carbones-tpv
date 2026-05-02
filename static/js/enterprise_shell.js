/**
 * Carbones y Pollos - Enterprise Shell v2.5
 * Centralized Industrial Orchestrator
 */

const EnterpriseShell = {
    modules: [
        { id: 'Portal', icon: '🏠', path: '/static/portal.html', category: 'Core' },
        { id: 'Caja', icon: '💰', path: '/static/caja.html', category: 'Core' },
        { id: 'KDS', icon: '🍳', path: '/static/kds.html', category: 'Core' },
        { id: 'Producción', icon: '🔥', path: '/static/dashboard_produccion.html', category: 'Core' },
        { id: 'Reservas', icon: '🍷', path: '/static/reservas.html', category: 'Core' },
        
        { id: 'Stock', icon: '📦', path: '/static/inventario.html', category: 'Logistics' },
        { id: 'Proveedores', icon: '🏭', path: '/static/proveedores.html', category: 'Logistics' },
        { id: 'Reparto', icon: '🛵', path: '/static/reparto.html', category: 'Logistics' },
        { id: 'Procurement', icon: '📦', path: '/static/procurement.html', category: 'Logistics' },
        { id: 'Aggregators', icon: '🍔', path: '/static/delivery_aggregators.html', category: 'Logistics' },
        { id: 'Fleet', icon: '🚚', path: '/static/fleet.html', category: 'Logistics' },
        
        { id: 'Analytics', icon: '📊', path: '/static/analytics.html', category: 'Management' },
        { id: 'ERP', icon: '💼', path: '/static/erp.html', category: 'Management' },
        { id: 'RRHH', icon: '👥', path: '/static/rrhh.html', category: 'Management' },
        { id: 'Marketing', icon: '📣', path: '/static/marketing.html', category: 'Management' },
        { id: 'Referidos', icon: '🔗', path: '/static/referidos.html', category: 'Management' },
        { id: 'Franquicias', icon: '🏢', path: '/static/franchise.html', category: 'Management' },
        { id: 'ESG & Eco', icon: '🌱', path: '/static/esg.html', category: 'Management' },
        { id: 'Menu Eng.', icon: '🧠', path: '/static/menu_engineering.html', category: 'Management' },
        { id: 'B2B Sales', icon: '🤝', path: '/static/commercial.html', category: 'Management' },
        { id: 'Loyalty', icon: '🏆', path: '/static/loyalty.html', category: 'Management' },
        
        { id: 'Ajustes', icon: '⚙️', path: '/static/settings.html', category: 'System' },
        { id: 'Auditoría', icon: '🛡️', path: '/static/auditoria.html', category: 'System' },
        { id: 'IoT Equipos', icon: '🌡️', path: '/static/iot.html', category: 'System' },
        { id: 'Crisis', icon: '🚨', path: '/static/crisis.html', category: 'System' },
        { id: 'Maintenance', icon: '🛠️', path: '/static/mantenimiento.html', category: 'System' },
        { id: 'Hardware', icon: '🖨️', path: '/static/hardware.html', category: 'System' }
    ],

    init(activeId) {
        if (!activeId) {
            activeId = document.body.getAttribute('data-active-module') || 'Portal';
        }
        this.renderSidebar(activeId);
        this.injectGlobalStyles();
        this.startTelemetry();
        console.log(`[Enterprise Shell] Module "${activeId}" initialized.`);
    },

    startTelemetry() {
        // Mock telemetry for industrial feel
        setInterval(() => {
            const latency = Math.floor(Math.random() * 50) + 10;
            const latencyEl = document.getElementById('shell-latency');
            if (latencyEl) latencyEl.innerText = `${latency}ms`;
        }, 5000);
    },

    renderSidebar(activeId) {
        const sidebar = document.getElementById('enterprise-sidebar');
        if (!sidebar) return;

        sidebar.className = "w-24 lg:w-72 bg-white border-r border-slate-100 flex flex-col p-6 h-full transition-all duration-500 ease-in-out";
        
        let html = `
            <div class="flex items-center gap-4 mb-16 px-2">
                <div class="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-indigo-100">🍗</div>
                <div class="hidden lg:block">
                    <h2 class="text-sm font-black text-slate-900 uppercase tracking-tighter">Carbones <span class="text-indigo-600">Pro</span></h2>
                    <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Industrial Node v2.5</p>
                </div>
            </div>
            <nav class="flex-1 space-y-1 overflow-y-auto custom-scrollbar pr-2">
        `;

        const categories = [...new Set(this.modules.map(m => m.category))];
        
        categories.forEach(cat => {
            html += `<p class="hidden lg:block text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 mt-8 px-2">${cat}</p>`;
            this.modules.filter(m => m.category === cat).forEach(m => {
                const isActive = m.id === activeId;
                html += `
                    <a href="${m.path}" class="flex items-center gap-4 p-4 rounded-2xl transition-all duration-300 group ${isActive ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100' : 'text-slate-500 hover:bg-slate-50'}">
                        <span class="text-xl">${m.icon}</span>
                        <span class="hidden lg:block text-xs font-black uppercase tracking-tight">${m.id}</span>
                    </a>
                `;
            });
        });

        html += `
            </nav>
            <div class="mt-10 pt-10 border-t border-slate-50 px-2">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center text-white text-[10px] font-black">AD</div>
                    <div class="hidden lg:block">
                        <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Master Admin</p>
                        <p class="text-[10px] font-black text-slate-900 uppercase truncate">Admin Panel</p>
                    </div>
                </div>
                <div class="mt-4 flex items-center justify-between px-2">
                    <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest">Status: <span class="text-emerald-500">Online</span></span>
                    <span id="shell-latency" class="text-[8px] font-black text-slate-400 uppercase tracking-widest">--ms</span>
                </div>
            </div>
        `;

        sidebar.innerHTML = html;
    },

    injectGlobalStyles() {
        if (document.getElementById('shell-global-styles')) return;
        const style = document.createElement('style');
        style.id = 'shell-global-styles';
        style.textContent = `
            .bg-grid-industrial {
                position: fixed; inset: 0; z-index: -1; pointer-events: none;
                background-size: 60px 60px;
                background-image: linear-gradient(to right, rgba(0,0,0,0.02) 1px, transparent 1px),
                                linear-gradient(to bottom, rgba(0,0,0,0.02) 1px, transparent 1px);
            }
            .glass-panel {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 10px 40px -15px rgba(0, 0, 0, 0.05);
            }
            .custom-scrollbar::-webkit-scrollbar { width: 4px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            main { animation: fadeIn 0.6s ease-out forwards; }
        `;
        document.head.appendChild(style);
    },

    showToast(title, message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-10 right-10 z-[9999] glass-panel p-6 rounded-2xl flex items-center gap-4 animate-in border-l-4 ${type === 'success' ? 'border-l-emerald-500' : 'border-l-rose-500'}`;
        toast.innerHTML = `
            <div class="w-10 h-10 rounded-full flex items-center justify-center bg-slate-50 text-lg">${type === 'success' ? '✅' : '⚠️'}</div>
            <div>
                <p class="text-xs font-black text-slate-900 uppercase tracking-tighter">${title}</p>
                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">${message}</p>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
};

window.EnterpriseShell = EnterpriseShell;
