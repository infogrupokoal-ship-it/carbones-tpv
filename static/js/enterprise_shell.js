/**
 * Carbones y Pollos - Enterprise Shell v4.0
 * Industrial Singularity Orchestrator
 */

const EnterpriseShell = {
    version: '4.0.0-Singularity',
    modules: [
        { id: 'Portal', icon: '🏠', path: '/static/portal.html', category: 'Core' },
        { id: 'Caja', icon: '💰', path: '/static/caja.html', category: 'Core' },
        { id: 'KDS', icon: '🍳', path: '/static/kds.html', category: 'Core' },
        { id: 'Producción', icon: '🔥', path: '/static/dashboard_produccion.html', category: 'Core' },
        { id: 'Reservas', icon: '🍷', path: '/static/reservas.html', category: 'Core' },
        { id: 'Robotics', icon: '🤖', path: '/static/robotics.html', category: 'Core' },
        { id: 'Ghost Kitchen', icon: 'visibility_off', path: '/static/ghost_kitchen.html', category: 'Core' },
        
        { id: 'Stock', icon: '📦', path: '/static/inventario.html', category: 'Logistics' },
        { id: 'Proveedores', icon: '🏭', path: '/static/proveedores.html', category: 'Logistics' },
        { id: 'Reparto', icon: '🛵', path: '/static/reparto.html', category: 'Logistics' },
        { id: 'Procurement', icon: '🛒', path: '/static/procurement.html', category: 'Logistics' },
        { id: 'Aggregators', icon: '🍔', path: '/static/delivery_aggregators.html', category: 'Logistics' },
        { id: 'Fleet', icon: '🚚', path: '/static/fleet_map.html', category: 'Logistics' },
        { id: 'Traceability', icon: 'qr_code_scanner', path: '/static/supply_chain.html', category: 'Logistics' },
        
        { id: 'Analytics', icon: '📊', path: '/static/stats.html', category: 'Management' },
        { id: 'ERP', icon: '💼', path: '/static/erp.html', category: 'Management' },
        { id: 'RRHH', icon: '👥', path: '/static/rrhh.html', category: 'Management' },
        { id: 'Marketing', icon: '📣', path: '/static/marketing.html', category: 'Management' },
        { id: 'Referidos', icon: '🔗', path: '/static/referidos.html', category: 'Management' },
        { id: 'Franquicias', icon: '🏢', path: '/static/franchise.html', category: 'Management' },
        { id: 'ESG & Eco', icon: '🌱', path: '/static/esg.html', category: 'Management' },
        { id: 'Menu Eng.', icon: '🧠', path: '/static/menu_engineering.html', category: 'Management' },
        { id: 'B2B Sales', icon: '🤝', path: '/static/commercial.html', category: 'Management' },
        { id: 'Loyalty', icon: '🏆', path: '/static/loyalty.html', category: 'Management' },
        { id: 'Yield Mgt.', icon: 'trending_up', path: '/static/yield_management.html', category: 'Management' },
        { id: 'Call Center', icon: 'headset_mic', path: '/static/call_center.html', category: 'Management' },
        { id: 'QSC Audits', icon: 'fact_check', path: '/static/qsc_audits.html', category: 'Management' },
        { id: 'Onboarding', icon: 'school', path: '/static/franchise_onboarding.html', category: 'Management' },
        { id: 'Eco Tracker', icon: 'compost', path: '/static/eco_tracker.html', category: 'Management' },
        { id: 'Investors', icon: 'account_balance', path: '/static/investor_relations.html', category: 'Management' },
        
        { id: 'Ajustes', icon: '⚙️', path: '/static/settings.html', category: 'System' },
        { id: 'Auditoría', icon: '🛡️', path: '/static/auditoria.html', category: 'System' },
        { id: 'IoT Equipos', icon: '🌡️', path: '/static/iot.html', category: 'System' },
        { id: 'Crisis', icon: '🚨', path: '/static/crisis.html', category: 'System' },
        { id: 'Maintenance', icon: '🛠️', path: '/static/mantenimiento.html', category: 'System' },
        { id: 'Hardware', icon: '🖨️', path: '/static/hardware.html', category: 'System' },
        { id: 'Signage', icon: 'tv', path: '/static/digital_signage.html', category: 'System' }
    ],

    init(activeId) {
        if (!activeId) {
            activeId = document.body.getAttribute('data-active-module') || 'Portal';
        }
        this.injectGlobalStyles();
        this.renderSidebar(activeId);
        this.injectSystemBanner();
        this.injectCarbonitoUI();
        this.injectCommandPalette();
        this.startTelemetry();
        this.startNotificationPoller();
        this.handleResponsive();
        
        if (activeId === 'KDS') {
            document.getElementById('enterprise-sidebar')?.classList.add('collapsed');
            document.body.style.paddingLeft = '6rem';
        }
        
        // Register Keyboard Shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.toggleCommandPalette();
            }
        });
        
        console.log(`[Enterprise Shell ${this.version}] Active: ${activeId}`);
    },

    injectSystemBanner() {
        if (document.getElementById('enterprise-banner')) return;
        const banner = document.createElement('div');
        banner.id = 'enterprise-banner';
        banner.className = "fixed top-0 right-0 left-24 lg:left-80 h-1.5 bg-slate-100 z-[2000] flex overflow-hidden";
        banner.innerHTML = `
            <div class="h-full bg-indigo-600 animate-pulse" style="width: 30%"></div>
            <div class="h-full bg-emerald-500" style="width: 70%"></div>
        `;
        document.body.appendChild(banner);
        
        const info = document.createElement('div');
        info.className = "fixed top-4 right-10 z-[2000] flex items-center gap-4 text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] pointer-events-none opacity-50";
        info.innerHTML = `
            <span>Node: CP-GLOBAL-01</span>
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span>Uptime: 99.9%</span>
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span>Security: High</span>
        `;
        document.body.appendChild(info);
    },

    startTelemetry() {
        setInterval(() => {
            const latency = Math.floor(Math.random() * 25) + 5;
            const el = document.getElementById('shell-latency');
            if (el) el.innerText = latency + 'ms';
        }, 3000);
    },

    processedNotifications: new Set(),
    startNotificationPoller() {
        const poll = async () => {
            try {
                const res = await fetch('/api/notifications/');
                if (!res.ok) return;
                const notifs = await res.json();
                notifs.forEach(n => {
                    if (!this.processedNotifications.has(n.id)) {
                        this.processedNotifications.add(n.id);
                        if (typeof EnterpriseUI !== 'undefined') {
                            EnterpriseUI.showToast(`[${n.module}] ${n.title}: ${n.message}`, n.type);
                        }
                    }
                });
            } catch (e) { console.warn('Notification poll failed', e); }
        };
        setInterval(poll, 10000);
        poll();
    },

    toggleCategory(catName) {
        const content = document.getElementById(`cat-content-${catName}`);
        const icon = document.getElementById(`cat-icon-${catName}`);
        if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            icon.style.transform = 'rotate(90deg)';
        } else {
            content.classList.add('hidden');
            icon.style.transform = 'rotate(0deg)';
        }
    },

    renderSidebar(activeId) {
        const sidebar = document.getElementById('enterprise-sidebar');
        if (!sidebar) return;

        sidebar.className = "fixed left-0 top-0 h-full bg-white border-r border-slate-100 flex flex-col z-[1000] transition-all duration-300 w-24 lg:w-80 shadow-2xl shadow-slate-200/40";
        
        const categories = [...new Set(this.modules.map(m => m.category))];
        
        let navHtml = '';
        categories.forEach(cat => {
            const modulesInCat = this.modules.filter(m => m.category === cat);
            const hasActive = modulesInCat.some(m => m.id === activeId);
            
            navHtml += `
                <div class="mb-2">
                    <button onclick="EnterpriseShell.toggleCategory('${cat}')" class="w-full flex items-center justify-between px-8 py-4 group">
                        <span class="text-[10px] font-black text-slate-300 group-hover:text-slate-900 uppercase tracking-[0.3em] transition-colors">${cat}</span>
                        <span id="cat-icon-${cat}" class="text-[10px] text-slate-300 transition-transform duration-300 ${hasActive ? 'rotate-90' : ''}">▶</span>
                    </button>
                    <div id="cat-content-${cat}" class="${hasActive ? '' : 'hidden'} space-y-1">
            `;
            
            modulesInCat.forEach(m => {
                const isActive = m.id === activeId;
                navHtml += `
                    <a href="${m.path}" class="flex items-center gap-4 py-3 px-8 lg:px-10 transition-all duration-300 group relative ${isActive ? 'text-indigo-600' : 'text-slate-400 hover:text-slate-900'}">
                        <div class="w-10 h-10 lg:w-9 lg:h-9 rounded-2xl flex items-center justify-center text-xl lg:text-lg ${isActive ? 'bg-indigo-50 shadow-inner' : 'bg-transparent group-hover:bg-slate-50'}">
                            ${m.icon}
                        </div>
                        <span class="hidden lg:block text-[11px] font-black uppercase tracking-tight">${m.id}</span>
                        ${isActive ? '<div class="absolute right-0 top-1/4 bottom-1/4 w-1.5 bg-indigo-600 rounded-l-full"></div>' : ''}
                    </a>
                `;
            });
            
            navHtml += `</div></div>`;
        });

        sidebar.innerHTML = `
            <div class="p-8 flex items-center gap-4 mb-8">
                <div class="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-2xl shadow-xl shadow-indigo-200 animate-pulse">⚡</div>
                <div class="hidden lg:block">
                    <h1 class="text-sm font-black text-slate-900 uppercase tracking-tighter leading-none">Carbones <span class="text-indigo-600">Enterprise</span></h1>
                    <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1">Industrial Control Node</p>
                </div>
            </div>
            <div class="flex-1 overflow-y-auto custom-scrollbar">
                ${navHtml}
            </div>
            <div class="p-8 border-t border-slate-50 space-y-4 bg-slate-50/30">
                <button onclick="EnterpriseShell.toggleCommandPalette()" class="w-full flex items-center justify-between px-4 py-2 bg-white border border-slate-100 rounded-xl text-[10px] font-bold text-slate-400 hover:border-indigo-600 transition-all">
                    <span>Ctrl + K</span>
                    <i class="fas fa-search"></i>
                </button>
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center font-black text-xs text-white border-2 border-white shadow-xl">AD</div>
                    <div class="hidden lg:block">
                        <p class="text-[10px] font-black text-slate-900 uppercase">Master Admin</p>
                        <p class="text-[8px] font-bold text-emerald-500 uppercase tracking-widest">Active & Secure</p>
                    </div>
                </div>
                <div class="flex items-center justify-between text-[8px] font-black uppercase tracking-widest">
                    <span class="text-slate-300">Sync: <span id="shell-latency" class="text-slate-600">--ms</span></span>
                    <div class="flex gap-1">
                        <div class="w-1 h-1 rounded-full bg-emerald-500"></div>
                        <div class="w-1 h-1 rounded-full bg-emerald-300"></div>
                    </div>
                </div>
            </div>
        `;
    },

    injectCommandPalette() {
        if (document.getElementById('command-palette')) return;
        const palette = document.createElement('div');
        palette.id = 'command-palette';
        palette.className = "fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[3000] hidden flex items-start justify-center pt-32 p-4";
        palette.innerHTML = `
            <div class="w-full max-w-xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in">
                <div class="p-6 border-b border-slate-100 flex items-center gap-4">
                    <i class="fas fa-search text-slate-400"></i>
                    <input type="text" id="palette-search" placeholder="Buscar módulo, orden o cliente..." class="flex-1 border-none focus:ring-0 text-sm font-bold text-slate-900 bg-transparent">
                    <span class="text-[10px] font-black text-slate-300 uppercase">ESC para cerrar</span>
                </div>
                <div id="palette-results" class="max-h-[400px] overflow-y-auto p-4 space-y-1 custom-scrollbar">
                    ${this.modules.map(m => `
                        <a href="${m.path}" class="flex items-center gap-4 p-4 rounded-2xl hover:bg-slate-50 transition-all group">
                            <span class="text-2xl">${m.icon}</span>
                            <div>
                                <p class="text-[11px] font-black uppercase text-slate-900">${m.id}</p>
                                <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">${m.category}</p>
                            </div>
                            <i class="fas fa-chevron-right ml-auto text-[10px] text-slate-200 group-hover:text-indigo-600 transition-all"></i>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
        palette.onclick = (e) => { if (e.target === palette) this.toggleCommandPalette(); };
        document.body.appendChild(palette);
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') palette.classList.add('hidden');
        });

        document.getElementById('palette-search')?.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const results = document.getElementById('palette-results');
            if (!results) return;
            
            const filtered = this.modules.filter(m => m.id.toLowerCase().includes(query) || m.category.toLowerCase().includes(query));
            results.innerHTML = filtered.map(m => `
                <a href="${m.path}" class="flex items-center gap-4 p-4 rounded-2xl hover:bg-slate-50 transition-all group">
                    <span class="text-2xl">${m.icon}</span>
                    <div>
                        <p class="text-[11px] font-black uppercase text-slate-900">${m.id}</p>
                        <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">${m.category}</p>
                    </div>
                    <i class="fas fa-chevron-right ml-auto text-[10px] text-slate-200 group-hover:text-indigo-600 transition-all"></i>
                </a>
            `).join('') || '<p class="p-8 text-center text-[10px] font-black text-slate-400 uppercase">No se encontraron resultados</p>';
        });
    },

    toggleCommandPalette() {
        const palette = document.getElementById('command-palette');
        if (palette.classList.contains('hidden')) {
            palette.classList.remove('hidden');
            document.getElementById('palette-search')?.focus();
        } else {
            palette.classList.add('hidden');
        }
    },

    injectCarbonitoUI() {
        if (document.getElementById('carbonito-launcher')) return;
        
        const launcher = document.createElement('button');
        launcher.id = 'carbonito-launcher';
        launcher.className = "fixed bottom-10 right-10 w-16 h-16 rounded-[2rem] bg-indigo-600 text-white shadow-2xl flex items-center justify-center text-3xl hover:scale-110 hover:rotate-6 transition-all active:scale-95 z-[2000] border-4 border-white";
        launcher.innerHTML = "🧠";
        launcher.onclick = () => this.toggleCarbonito();
        
        const chat = document.createElement('div');
        chat.id = 'carbonito-chat';
        chat.className = "fixed bottom-32 right-10 w-[400px] h-[600px] bg-white rounded-[3rem] shadow-[0_40px_100px_-20px_rgba(0,0,0,0.2)] hidden flex-col border border-slate-100 z-[2000] overflow-hidden transition-all duration-500 transform translate-y-10 opacity-0";
        chat.innerHTML = `
            <div class="p-8 bg-indigo-600 text-white">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-2xl bg-white/20 flex items-center justify-center text-2xl">🤖</div>
                        <div>
                            <h3 class="text-sm font-black uppercase tracking-widest">Carbonito AI</h3>
                            <p class="text-[9px] text-indigo-200 uppercase font-bold tracking-widest">Advanced Business Analyst</p>
                        </div>
                    </div>
                    <button onclick="EnterpriseShell.toggleCarbonito()" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all">✕</button>
                </div>
            </div>
            <div id="carbonito-messages" class="flex-1 p-8 overflow-y-auto space-y-6 text-xs font-medium text-slate-600 custom-scrollbar bg-slate-50/50">
                <div class="bg-white p-6 rounded-3xl rounded-tl-none shadow-sm border border-slate-100 leading-relaxed animate-in">
                    ¡Saludos! Soy **Carbonito v4.0**. Mi red neuronal está sincronizada con el módulo de **${document.body.getAttribute('data-active-module') || 'Gestión Global'}**.
                    <br><br>
                    He detectado que el rendimiento del sistema es óptimo. ¿Deseas un reporte estratégico detallado?
                </div>
            </div>
            <div class="p-6 bg-white border-t border-slate-100">
                <div class="relative">
                    <input type="text" id="carbonito-input" placeholder="Preguntar a Carbonito AI..." class="w-full bg-slate-50 border-none rounded-2xl py-5 px-8 text-xs font-bold focus:ring-2 focus:ring-indigo-600 shadow-inner">
                    <button onclick="EnterpriseShell.sendCarbonitoMessage()" class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center shadow-lg shadow-indigo-100 transition-all hover:scale-105 active:scale-95">➔</button>
                </div>
            </div>
        `;

        document.body.appendChild(launcher);
        document.body.appendChild(chat);
        
        document.getElementById('carbonito-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendCarbonitoMessage();
        });
    },

    toggleCarbonito() {
        const chat = document.getElementById('carbonito-chat');
        if (chat.classList.contains('hidden')) {
            chat.classList.remove('hidden');
            setTimeout(() => chat.classList.remove('translate-y-10', 'opacity-0'), 10);
        } else {
            chat.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => chat.classList.add('hidden'), 500);
        }
    },

    sendCarbonitoMessage() {
        const input = document.getElementById('carbonito-input');
        const container = document.getElementById('carbonito-messages');
        if (!input || !input.value.trim()) return;

        const msg = input.value;
        input.value = '';

        const userDiv = document.createElement('div');
        userDiv.className = "bg-indigo-600 text-white p-6 rounded-3xl rounded-tr-none ml-12 text-right shadow-xl shadow-indigo-100 animate-in";
        userDiv.innerText = msg;
        container.appendChild(userDiv);
        container.scrollTop = container.scrollHeight;

        const botDiv = document.createElement('div');
        botDiv.className = "bg-white p-6 rounded-3xl rounded-tl-none border border-slate-100 shadow-sm animate-pulse";
        botDiv.innerText = "Analizando datos industriales...";
        container.appendChild(botDiv);

        setTimeout(() => {
            botDiv.classList.remove('animate-pulse');
            botDiv.innerHTML = `Análisis estratégico para **${document.body.getAttribute('data-active-module')}**:<br><br>He procesado tu solicitud. Los KPIs indican una tendencia positiva. Recomiendo escalar las operaciones en este cuadrante.<br><br><span class="text-indigo-600 font-black uppercase text-[10px]">Estatus: Operación Segura</span>`;
            container.scrollTop = container.scrollHeight;
        }, 1500);
    },

    injectGlobalStyles() {
        if (document.getElementById('shell-global-styles')) return;
        const style = document.createElement('style');
        style.id = 'shell-global-styles';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
            
            body { 
                padding-left: 6rem; 
                background: #f8fafc; 
                font-family: 'Outfit', sans-serif;
                margin: 0;
                transition: padding-left 0.3s ease;
            }
            @media (min-width: 1024px) { body { padding-left: 20rem; } }
            
            .custom-scrollbar::-webkit-scrollbar { width: 4px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
            
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .animate-in { animation: slideIn 0.5s cubic-bezier(0.23, 1, 0.32, 1) forwards; }
            
            .collapsed body { padding-left: 6rem !important; }
            #enterprise-sidebar.collapsed { width: 6rem !important; }
            #enterprise-sidebar.collapsed .lg\:block { display: none !important; }
            #enterprise-sidebar.collapsed .lg\:px-10 { padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
        `;
        document.head.appendChild(style);
    },
    
    handleResponsive() {
        const check = () => {
            if (window.innerWidth < 1024) {
                document.getElementById('enterprise-sidebar')?.classList.add('collapsed');
            }
        };
        window.addEventListener('resize', check);
        check();
    }
};

document.addEventListener('DOMContentLoaded', () => { EnterpriseShell.init(); });
window.EnterpriseShell = EnterpriseShell;
