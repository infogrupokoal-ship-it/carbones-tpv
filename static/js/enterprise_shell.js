/**
 * Carbones y Pollos - Enterprise Shell v5.1
 * Quantum Singularity Orchestrator - Industrial Grade
 */

const EnterpriseShell = {
    version: '5.1.0-Quantum',
    modules: [
        { id: 'Analytics', icon: '📈', path: '/static/predictive_analytics.html', category: 'Core' },
        { id: 'Matrix', icon: '🌌', path: '/static/matrix.html', category: 'Core' },
        { id: 'Portal', icon: '🏠', path: '/static/portal.html', category: 'Core' },
        { id: 'Caja', icon: '💰', path: '/static/financial.html', category: 'Core' },
        { id: 'KDS', icon: '🍳', path: '/static/kds.html', category: 'Core' },
        { id: 'Dashboard', icon: '📊', path: '/static/dashboard.html', category: 'Core' },
        { id: 'Engines', icon: '⚙️', path: '/static/engines.html', category: 'Core' },
        
        { id: 'Stock', icon: '📦', path: '/static/stock.html', category: 'Logistics' },
        { id: 'Proveedores', icon: '🏭', path: '/static/proveedores.html', category: 'Logistics' },
        { id: 'Reparto', icon: '🛵', path: '/static/reparto.html', category: 'Logistics' },
        { id: 'Procurement', icon: '🛒', path: '/static/procurement.html', category: 'Logistics' },
        { id: 'Fleet', icon: '🚚', path: '/static/fleet_map.html', category: 'Logistics' },
        { id: 'Traceability', icon: '🔍', path: '/static/supply_chain.html', category: 'Logistics' },
        { id: 'Aggregators', icon: '🍔', path: '/static/delivery_aggregators.html', category: 'Logistics' },
        
        { id: 'ERP', icon: '💼', path: '/static/erp.html', category: 'Management' },
        { id: 'RRHH', icon: '👥', path: '/static/rrhh.html', category: 'Management' },
        { id: 'Marketing', icon: '📣', path: '/static/marketing.html', category: 'Management' },
        { id: 'Referidos', icon: '🔗', path: '/static/referidos.html', category: 'Management' },
        { id: 'Franquicias', icon: '🏢', path: '/static/franchise.html', category: 'Management' },
        { id: 'ESG & Eco', icon: '🌱', path: '/static/esg.html', category: 'Management' },
        { id: 'Menu Eng.', icon: '📜', path: '/static/menu_engineering.html', category: 'Management' },
        { id: 'B2B Sales', icon: '🤝', path: '/static/commercial.html', category: 'Management' },
        { id: 'Loyalty', icon: '🏆', path: '/static/loyalty.html', category: 'Management' },
        { id: 'Yield Mgt.', icon: '📈', path: '/static/yield_management.html', category: 'Management' },
        { id: 'Call Center', icon: '🎧', path: '/static/call_center.html', category: 'Management' },
        { id: 'QSC Audits', icon: '✅', path: '/static/qsc_audits.html', category: 'Management' },
        { id: 'Investors', icon: '🏦', path: '/static/investor_relations.html', category: 'Management' },
        
        { id: 'Auditoría', icon: '🛡️', path: '/static/auditoria.html', category: 'System' },
        { id: 'IoT Equipos', icon: '🌡️', path: '/static/iot.html', category: 'System' },
        { id: 'Crisis', icon: '🚨', path: '/static/crisis.html', category: 'System' },
        { id: 'Maintenance', icon: '🛠️', path: '/static/mantenimiento.html', category: 'System' },
        { id: 'Hardware', icon: '🖨️', path: '/static/hardware.html', category: 'System' },
        { id: 'Robotics', icon: '🤖', path: '/static/robotics.html', category: 'System' },
        { id: 'Settings', icon: '⚙️', path: '/static/settings.html', category: 'System' }
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
        this.injectNeuralMonitor();
        this.startTelemetry();
        this.startNotificationPoller();
        this.handleResponsive();
        
        if (activeId === 'KDS' || activeId === 'Matrix') {
            document.getElementById('enterprise-sidebar')?.classList.add('collapsed');
            document.body.style.paddingLeft = '6rem';
        }
        
        // Shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') { e.preventDefault(); this.toggleCommandPalette(); }
            if (e.ctrlKey && e.key === 'j') { e.preventDefault(); this.toggleNeuralMonitor(); }
        });
        
        console.log(`[Enterprise Shell ${this.version}] Initiated.`);
    },

    injectSystemBanner() {
        if (document.getElementById('enterprise-banner')) return;
        const banner = document.createElement('div');
        banner.id = 'enterprise-banner';
        banner.className = "fixed top-0 right-0 left-24 lg:left-80 h-1 bg-slate-100 z-[2000] flex overflow-hidden";
        banner.innerHTML = `<div id="shell-progress-bar" class="h-full bg-indigo-600 transition-all duration-1000" style="width: 100%"></div>`;
        document.body.appendChild(banner);
        
        const info = document.createElement('div');
        info.className = "fixed top-4 right-10 z-[2000] flex items-center gap-4 text-[8px] font-black text-slate-400 uppercase tracking-[0.2em] pointer-events-none select-none";
        info.innerHTML = `
            <span id="shell-node-id">CP-QUANTUM-NODE-01</span>
            <span class="w-1 h-1 rounded-full bg-slate-200"></span>
            <span id="shell-clock">00:00:00</span>
        `;
        document.body.appendChild(info);
        setInterval(() => {
            document.getElementById('shell-clock').innerText = new Date().toLocaleTimeString('es-ES', {hour12: false});
        }, 1000);
    },

    injectNeuralMonitor() {
        if (document.getElementById('neural-monitor')) return;
        const monitor = document.createElement('div');
        monitor.id = 'neural-monitor';
        monitor.className = "fixed top-0 right-0 w-[400px] h-screen bg-slate-900 text-slate-400 font-mono text-[10px] p-8 z-[2500] transform translate-x-full transition-transform duration-500 shadow-2xl border-l border-white/10 overflow-hidden hidden lg:block";
        monitor.innerHTML = `
            <div class="flex justify-between items-center mb-8">
                <span class="text-white font-black uppercase tracking-widest">Neural Stream</span>
                <button onclick="EnterpriseShell.toggleNeuralMonitor()" class="text-slate-600 hover:text-white">✕</button>
            </div>
            <div id="neural-logs" class="space-y-2 overflow-y-auto h-[80vh] custom-scrollbar">
                <div class="text-indigo-400">[INIT] Attaching to local quantum node...</div>
            </div>
            <div class="mt-8 pt-8 border-t border-white/5 grid grid-cols-2 gap-4">
                <div>
                    <p class="text-[8px] uppercase font-black mb-1">CPU Load</p>
                    <div class="h-1 bg-white/5 rounded-full overflow-hidden">
                        <div id="neural-cpu" class="h-full bg-indigo-500" style="width: 24%"></div>
                    </div>
                </div>
                <div>
                    <p class="text-[8px] uppercase font-black mb-1">Neural Flux</p>
                    <div class="h-1 bg-white/5 rounded-full overflow-hidden">
                        <div id="neural-flux" class="h-full bg-emerald-500" style="width: 68%"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(monitor);
    },

    toggleNeuralMonitor() {
        const mon = document.getElementById('neural-monitor');
        mon.classList.toggle('translate-x-full');
    },

    startTelemetry() {
        setInterval(async () => {
            try {
                const res = await fetch('/api/health');
                const data = await res.json();
                
                const latencyEl = document.getElementById('shell-latency');
                if (latencyEl) latencyEl.innerText = `${data.telemetry.database.latency_ms.toFixed(2)}ms`;
                
                const cpuEl = document.getElementById('neural-cpu');
                if (cpuEl) cpuEl.style.width = `${data.telemetry.cpu_usage}%`;
                
                const fluxEl = document.getElementById('neural-flux');
                if (fluxEl) fluxEl.style.width = `${data.telemetry.memory_usage}%`;

                const nodeEl = document.getElementById('shell-node-id');
                if (nodeEl) nodeEl.innerText = data.deployment.node.toUpperCase();

                const log = document.createElement('div');
                log.className = "opacity-60";
                log.innerHTML = `<span class="text-slate-600">${new Date().toLocaleTimeString()}</span> <span class="text-indigo-400">[SYS]</span> DB_SYNC: OK | HEAL: ${data.integrity.self_healing}`;
                const logsCont = document.getElementById('neural-logs');
                if (logsCont) {
                    logsCont.appendChild(log);
                    logsCont.scrollTop = logsCont.scrollHeight;
                    if (logsCont.children.length > 50) logsCont.removeChild(logsCont.firstChild);
                }
            } catch(e) {
                console.warn("[Shell] Telemetry Sync Fail", e);
            }
        }, 3000);
    },

    startNotificationPoller() {
        const poll = async () => {
            try {
                const res = await fetch('/api/notifications/');
                if (res.ok) {
                    const notifs = await res.json();
                    notifs.forEach(n => {
                        if (typeof EnterpriseUI !== 'undefined') EnterpriseUI.showToast(n.message, n.type);
                    });
                }
            } catch (e) {}
        };
        setInterval(poll, 10000);
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
                    <h1 class="text-sm font-black text-slate-900 uppercase tracking-tighter leading-none">Carbones <span class="text-indigo-600">Quantum</span></h1>
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
                        <p class="text-[8px] font-bold text-emerald-500 uppercase tracking-widest">Quantum Secured</p>
                    </div>
                </div>
                <div class="flex items-center justify-between text-[8px] font-black uppercase tracking-widest">
                    <span class="text-slate-300">Sync: <span id="shell-latency" class="text-slate-600">--ms</span></span>
                    <div class="flex items-center gap-2">
                        <span class="text-[7px] text-emerald-500 animate-pulse">Singularity Active</span>
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
            <div class="w-full max-w-xl bg-white rounded-[3rem] shadow-2xl overflow-hidden animate-in">
                <div class="p-8 border-b border-slate-100 flex items-center gap-6">
                    <i class="fas fa-search text-slate-400 text-xl"></i>
                    <input type="text" id="palette-search" placeholder="Search anything in the ecosystem..." class="flex-1 border-none focus:ring-0 text-lg font-black text-slate-900 bg-transparent placeholder:text-slate-200">
                    <span class="text-[8px] font-black text-slate-300 uppercase">ESC</span>
                </div>
                <div id="palette-results" class="max-h-[400px] overflow-y-auto p-6 space-y-2 custom-scrollbar">
                    ${this.modules.map(m => `
                        <a href="${m.path}" class="flex items-center gap-6 p-5 rounded-3xl hover:bg-slate-50 transition-all group">
                            <span class="text-3xl">${m.icon}</span>
                            <div>
                                <p class="text-[12px] font-black uppercase text-slate-900">${m.id}</p>
                                <p class="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em]">${m.category}</p>
                            </div>
                            <i class="fas fa-arrow-right ml-auto text-slate-200 group-hover:text-indigo-600 transform group-hover:translate-x-1 transition-all"></i>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
        palette.onclick = (e) => { if (e.target === palette) this.toggleCommandPalette(); };
        document.body.appendChild(palette);
        
        document.getElementById('palette-search')?.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const results = document.getElementById('palette-results');
            const filtered = this.modules.filter(m => m.id.toLowerCase().includes(query) || m.category.toLowerCase().includes(query));
            results.innerHTML = filtered.map(m => `
                <a href="${m.path}" class="flex items-center gap-6 p-5 rounded-3xl hover:bg-slate-50 transition-all group">
                    <span class="text-3xl">${m.icon}</span>
                    <div>
                        <p class="text-[12px] font-black uppercase text-slate-900">${m.id}</p>
                        <p class="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em]">${m.category}</p>
                    </div>
                    <i class="fas fa-arrow-right ml-auto text-slate-200 group-hover:text-indigo-600 transform group-hover:translate-x-1 transition-all"></i>
                </a>
            `).join('') || '<div class="p-12 text-center opacity-30 font-black uppercase tracking-widest text-xs">Zero results found in matrix</div>';
        });
    },

    toggleCommandPalette() {
        const p = document.getElementById('command-palette');
        p.classList.toggle('hidden');
        if (!p.classList.contains('hidden')) document.getElementById('palette-search').focus();
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
        chat.className = "fixed bottom-32 right-10 w-[400px] h-[600px] bg-white rounded-[3.5rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.3)] hidden flex-col border border-slate-100 z-[2000] overflow-hidden transition-all duration-500 transform translate-y-10 opacity-0";
        chat.innerHTML = `
            <div class="p-10 bg-indigo-600 text-white relative overflow-hidden">
                <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
                <div class="flex items-center justify-between relative z-10">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl">🤖</div>
                        <div>
                            <h3 class="text-sm font-black uppercase tracking-[0.2em]">Carbonito <span class="text-indigo-200">AI</span></h3>
                            <p class="text-[8px] text-indigo-200 uppercase font-bold tracking-[0.3em]">Quantum Intelligence Layer</p>
                        </div>
                    </div>
                    <button onclick="EnterpriseShell.toggleCarbonito()" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-xs">✕</button>
                </div>
            </div>
            <div id="carbonito-messages" class="flex-1 p-10 overflow-y-auto space-y-6 text-[11px] font-bold text-slate-600 custom-scrollbar bg-slate-50/50">
                <div class="bg-white p-6 rounded-3xl rounded-tl-none shadow-sm border border-slate-100 leading-relaxed">
                    Protocolo **Singularity v5.1** iniciado. Estoy conectado al nodo central. ¿Qué optimización deseas ejecutar hoy?
                </div>
            </div>
            <div class="p-8 bg-white border-t border-slate-50">
                <div class="relative">
                    <input type="text" id="carbonito-input" placeholder="Consult quantum node..." class="w-full bg-slate-100 border-none rounded-3xl py-6 px-10 text-[11px] font-black focus:ring-2 focus:ring-indigo-600 shadow-inner">
                    <button id="carbonito-send-btn" onclick="EnterpriseShell.sendCarbonitoMessage()" class="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-indigo-600 text-white rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-100 hover:scale-105 active:scale-95 transition-all">➔</button>
                </div>
            </div>
        `;
        document.body.appendChild(launcher);
        document.body.appendChild(chat);
        document.getElementById('carbonito-input')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.sendCarbonitoMessage(); });
    },

    toggleCarbonito() {
        const c = document.getElementById('carbonito-chat');
        if (c.classList.contains('hidden')) {
            c.classList.remove('hidden');
            setTimeout(() => c.classList.remove('translate-y-10', 'opacity-0'), 10);
        } else {
            c.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => c.classList.add('hidden'), 500);
        }
    },

    async sendCarbonitoMessage() {
        const input = document.getElementById('carbonito-input');
        const cont = document.getElementById('carbonito-messages');
        const btn = document.getElementById('carbonito-send-btn');
        if (!input.value.trim()) return;
        const msg = input.value;
        input.value = '';
        
        const uDiv = document.createElement('div');
        uDiv.className = "bg-indigo-600 text-white p-6 rounded-3xl rounded-tr-none ml-12 text-right shadow-xl shadow-indigo-100 animate-in";
        uDiv.innerText = msg;
        cont.appendChild(uDiv);
        cont.scrollTop = cont.scrollHeight;

        const bDiv = document.createElement('div');
        bDiv.className = "bg-white p-6 rounded-3xl rounded-tl-none border border-slate-100 shadow-sm animate-pulse";
        bDiv.innerText = "Querying Matrix Data...";
        cont.appendChild(bDiv);
        cont.scrollTop = cont.scrollHeight;

        btn.disabled = true;

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, context: `Página actual: ${window.location.pathname}` })
            });
            const data = await res.json();
            
            bDiv.classList.remove('animate-pulse');
            bDiv.innerHTML = data.reply.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
            
            const metaDiv = document.createElement('p');
            metaDiv.className = "text-[7px] text-slate-300 mt-2 uppercase tracking-widest";
            metaDiv.innerText = `Model: ${data.model_used} | Tier: ${data.model_tier}`;
            bDiv.appendChild(metaDiv);
            
            cont.scrollTop = cont.scrollHeight;
        } catch(e) { 
            bDiv.innerText = "Quantum sync error. Matrix disconnected."; 
            bDiv.classList.remove('animate-pulse');
        } finally {
            btn.disabled = false;
        }
    },

    injectGlobalStyles() {
        if (document.getElementById('shell-global-styles')) return;
        const s = document.createElement('style');
        s.id = 'shell-global-styles';
        s.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
            body { padding-left: 6rem; background: #fbfcfe; font-family: 'Outfit', sans-serif; transition: padding-left 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
            @media (min-width: 1024px) { body { padding-left: 20rem; } }
            .custom-scrollbar::-webkit-scrollbar { width: 4px; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
            .animate-in { animation: slideIn 0.4s ease-out forwards; }
            .collapsed body { padding-left: 6rem !important; }
            #enterprise-sidebar.collapsed { width: 6rem !important; }
            #enterprise-sidebar.collapsed .lg\:block { display: none !important; }
            #enterprise-sidebar.collapsed .lg\:px-10 { padding-left: 1.5rem !important; }
        `;
        document.head.appendChild(s);
    },

    handleResponsive() {
        const h = () => { if (window.innerWidth < 1024) document.getElementById('enterprise-sidebar')?.classList.add('collapsed'); };
        window.addEventListener('resize', h); h();
    }
};

document.addEventListener('DOMContentLoaded', () => EnterpriseShell.init());
window.EnterpriseShell = EnterpriseShell;
