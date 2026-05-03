/**
 * Carbones y Pollos - Enterprise Shell v10.0
 * Quantum Singularity Orchestrator - Industrial Grade
 * Secured with RBAC & Neural Telemetry
 */

const EnterpriseShell = {
    version: '11.0.0-UEOS',
    user: null,
    modules: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊', path: '/static/dashboard.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'analytics', label: 'Analítica', icon: '📈', path: '/static/analytics.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'caja', label: 'Caja', icon: '💰', path: '/static/caja.html', roles: ['ADMIN', 'MANAGER', 'CASHIER'] },
        { id: 'inventario', label: 'Inventario', icon: '📦', path: '/static/inventario.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'tpv', label: 'TPV Terminal', icon: '🖥️', path: '/static/tpv.html', roles: ['ADMIN', 'MANAGER', 'CASHIER'] },
        { id: 'kds', label: 'Cocina KDS', icon: '👨‍🍳', path: '/static/kds.html', roles: ['ADMIN', 'MANAGER', 'KITCHEN'] },
        { id: 'matrix', label: 'Digital Twin', icon: '🌐', path: '/static/matrix.html', roles: ['ADMIN'] },
        { id: 'repartidores', label: 'Logística', icon: '🛵', path: '/static/repartidores.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'rrhh', label: 'Talent', icon: '🧬', path: '/static/rrhh.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'clientes', label: 'Fidelización', icon: '👥', path: '/static/loyalty.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'telemetria', label: 'Metrics', icon: '⚡', path: '/static/telemetria.html', roles: ['ADMIN'] },
        { id: 'config', label: 'Sistema', icon: '⚙️', path: '/static/settings.html', roles: ['ADMIN'] },
        { id: 'marketing', label: 'Marketing', icon: '🚀', path: '/static/marketing.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'financial', label: 'Finanzas', icon: '🏦', path: '/static/financial.html', roles: ['ADMIN', 'MANAGER'] },
        { id: 'multimedia', label: 'Archivos', icon: '📂', path: '/static/multimedia.html', roles: ['ADMIN', 'MANAGER'] }
    ],
    breadcrumb: ['Portal'],
    initialized: false,

    async checkAuth() {
        try {
            const token = localStorage.getItem('auth_token');
            const user = localStorage.getItem('auth_user');
            
            if (!token || !user) throw new Error("No token/user");

            const response = await fetch('/api/auth/me', {
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'X-Quantum-Profile': 'Handshake-v11'
                }
            });
            if (!response.ok) throw new Error("Session expired");
            this.user = await response.json();
            console.log(`[Auth] User authenticated: ${this.user.username} (${this.user.rol})`);
        } catch (e) {
            console.warn("[Auth] Guest mode active.");
            this.user = null;
        }
    },

    async init() {
        if (this.initialized) return;
        this.initialized = true;

        console.log("%c[QuantumShell] Starting Secure Core V11...", "color: #f59e0b; font-weight: bold;");
        await this.checkAuth();
        
        // Gatekeep check before rendering
        if (!this.gatekeep()) return;

        this.injectGlobalStyles();
        this.renderBase();
        this.updateBreadcrumbs();
        this.renderSecureUI();
        this.applyRoleShields();
        this.bindEvents();
        this.initKeyboardShortcuts();
        
        this.injectSystemBanner();
        this.injectCarbonitoUI();
        
        if (this.user && (this.user.rol === 'ADMIN' || this.user.rol === 'MANAGER')) {
            this.injectNeuralMonitor();
            this.injectCommandPalette();
            this.startTelemetry();
            this.pollNotifications();
            this.pollInsights();
        }

        // Handle browser navigation
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.moduleId) this.loadModule(e.state.moduleId, true);
        });
        
        console.log("%c[QuantumShell] Core Stabilized.", "color: #10b981; font-weight: bold;");
    },

    async loadModule(moduleId, skipPushState = false) {
        const module = this.modules.find(m => m.id === moduleId);
        if (!module) return;

        console.log(`[SPA] Loading module: ${moduleId}`);
        if (typeof EnterpriseUI !== 'undefined') {
            EnterpriseUI.showLoading(`Synapsing ${module.id} Node...`);
        }

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(module.path, {
                headers: { 
                    'X-SPA-Request': 'true',
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const content = doc.querySelector('#module-container') || doc.body;
            
            const container = document.getElementById('module-container');
            if (container) {
                container.style.opacity = '0';
                container.style.transform = 'translateY(10px)';
                
                setTimeout(() => {
                    container.innerHTML = content.innerHTML;
                    document.getElementById('module-title').innerText = module.label;
                    
                    // Update Breadcrumbs
                    this.breadcrumb = ['Portal', module.label];
                    this.updateBreadcrumbs();

                    // Update active state in nav
                    document.querySelectorAll('.nav-item').forEach(nav => {
                        nav.classList.toggle('active', nav.getAttribute('data-module') === moduleId);
                    });

                    // Re-run scripts
                    content.querySelectorAll('script').forEach(oldScript => {
                        const newScript = document.createElement('script');
                        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                        container.appendChild(newScript);
                    });

                    container.style.opacity = '1';
                    container.style.transform = 'translateY(0)';
                    if (typeof EnterpriseUI !== 'undefined') EnterpriseUI.hideLoading();
                    
                    // Smooth scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 400);

                if (!skipPushState) {
                    history.pushState({ moduleId }, module.label, module.path);
                }
            } else {
                window.location.href = module.path;
            }
        } catch (e) {
            console.error("Neural Link Interrupted:", e);
            if (typeof EnterpriseUI !== 'undefined') {
                EnterpriseUI.hideLoading();
                EnterpriseUI.notify("Neural Link Failure: " + e.message, "error");
            }
            window.location.href = module.path;
        }
        this.playSound('navigate');
    },

    updateBreadcrumbs() {
        const bc = document.getElementById('shell-breadcrumbs');
        if (!bc) return;
        bc.innerHTML = this.breadcrumb.map((b, i) => `
            <span class="bc-item ${i === this.breadcrumb.length - 1 ? 'current' : ''}">${b}</span>
            ${i < this.breadcrumb.length - 1 ? '<span class="bc-sep">/</span>' : ''}
        `).join('');
    },

    playSound(type) {
        const sounds = {
            navigate: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3',
            notif: 'https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3',
            alert: 'https://assets.mixkit.co/active_storage/sfx/2354/2354-preview.mp3'
        };
        const audio = new Audio(sounds[type]);
        audio.volume = 0.2;
        audio.play().catch(() => {}); // Autoplay policy bypass
    },

    gatekeep() {
        const path = window.location.pathname;
        if (path.includes('login.html') || path.includes('index.html') || path === '/') return true;

        if (!this.user) {
            console.error("[Gatekeeper] Unauthorized access detected. Redirecting to login.");
            window.location.href = '/static/login.html';
            return false;
        }

        const currentModule = this.modules.find(m => path.includes(m.path) || path.includes(m.id));
        if (currentModule && !currentModule.roles.includes(this.user.rol)) {
            console.error(`[Gatekeeper] Access Denied for role ${this.user.rol} on module ${currentModule.id}`);
            this.renderAccessDenied();
            return false;
        }
        return true;
    },

    renderAccessDenied() {
        const container = document.getElementById('module-container');
        if (container) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center min-h-[60vh] text-center p-8">
                    <div class="text-6xl mb-6">🚫</div>
                    <h2 class="text-3xl font-black text-slate-900 mb-2">ACCESO RESTRINGIDO</h2>
                    <p class="text-slate-500 max-w-md">Tu rol actual (<b>${this.user.rol}</b>) no tiene permisos para visualizar este módulo industrial.</p>
                    <button onclick="EnterpriseShell.loadModule('dashboard')" class="mt-8 bg-indigo-600 text-white px-8 py-3 rounded-2xl font-bold hover:shadow-xl transition-all">Volver al Panel Central</button>
                </div>
            `;
        }
    },

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+K for Search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleCommandPalette();
            }
            // Esc to close palette/monitor
            if (e.key === 'Escape') {
                document.getElementById('command-palette')?.classList.add('hidden');
                document.getElementById('neural-monitor')?.classList.add('translate-x-full');
                document.getElementById('carbonito-chat')?.classList.add('hidden');
            }
        });
    },

    filterModules(query) {
        const q = query.toLowerCase();
        document.querySelectorAll('.nav-item').forEach(nav => {
            const label = nav.querySelector('.nav-label')?.innerText.toLowerCase() || '';
            const matches = label.includes(q);
            nav.style.display = matches ? 'flex' : 'none';
        });
    },
    },

    applyRoleShields() {
        if (!this.user) return;
        const role = this.user.rol;
        document.querySelectorAll('[data-role]').forEach(el => {
            const allowedRoles = el.getAttribute('data-role').split(',');
            if (!allowedRoles.includes(role)) {
                el.style.display = 'none';
                el.remove(); // Seguridad extra eliminando el nodo
            }
        });
    },

    renderBase() {
        if (document.getElementById('quantum-shell')) return;
        const shell = document.createElement('div');
        shell.id = 'quantum-shell';
        shell.innerHTML = `
            <div id="neural-overlay"></div>
            <aside id="shell-sidebar">
                <div class="sidebar-brand">
                    <div class="brand-logo">🔥</div>
                    <span>SINGULARITY V11</span>
                </div>
                <div class="sidebar-search">
                    <input type="text" id="sidebar-module-search" placeholder="Buscar módulo... (Ctrl+K)" class="search-input">
                    <i class="fa-solid fa-magnifying-glass search-icon"></i>
                </div>
                <nav id="shell-nav">
                    <!-- Dynamic Nav -->
                </nav>
                <div class="sidebar-footer">
                    <div class="user-pill">
                        <div class="user-avatar">${this.user ? this.user.username[0].toUpperCase() : '?'}</div>
                        <div class="user-info">
                            <span class="user-name">${this.user ? this.user.full_name : 'Invitado'}</span>
                            <span class="user-role">${this.user ? this.user.rol : 'Sin Acceso'}</span>
                        </div>
                    </div>
                    ${this.user ? '<button id="btn-logout" class="btn-logout">Salir</button>' : '<a href="/login.html" class="btn-login">Login</a>'}
                </div>
            </aside>

            <main id="shell-viewport">
                <header id="shell-topbar">
                    <div class="topbar-left">
                        <button id="sidebar-toggle">☰</button>
                        <div class="flex flex-col">
                            <h1 id="module-title">Neural Matrix</h1>
                            <nav id="shell-breadcrumbs"></nav>
                        </div>
                    </div>
                    <div class="topbar-right">
                        <div id="neural-load" class="telemetry-item" style="display:none">
                            <span class="label">CPU</span>
                            <div class="bar-container"><div id="cpu-bar" class="bar" style="width: 0%"></div></div>
                        </div>
                        <div id="neural-latency" class="telemetry-item" style="display:none">
                            <span class="label">LAT</span>
                            <span id="latency-val" class="value">0ms</span>
                        </div>
                        <button id="btn-notifications" class="shell-icon-btn">
                            🔔<span id="notif-badge" class="notif-badge" style="display:none">0</span>
                        </button>
                        <button id="btn-command" class="shell-icon-btn" style="display:none">⌨️</button>
                    </div>
                </header>
                <section id="module-container">
                    <!-- App content -->
                </section>
            </main>

            <div id="notification-panel" class="shell-panel hidden">
                <div class="panel-header">
                    <h3>Centro de Control</h3>
                    <button class="close-panel" onclick="EnterpriseShell.toggleNotifications()">×</button>
                </div>
                <div id="notif-list" class="panel-body">
                    <div class="empty-state">No hay alertas activas.</div>
                </div>
            </div>
        `;
        document.body.appendChild(shell);
    },

    renderSecureUI() {
        const nav = document.getElementById('shell-nav');
        if (!nav) return;

        const currentPath = window.location.pathname;

        nav.innerHTML = this.modules
            .filter(m => !this.user || m.roles.includes(this.user.rol))
            .map(m => `
                <a href="${m.path}" class="nav-item ${currentPath.includes(m.id) ? 'active' : ''}" data-module="${m.id}">
                    <span class="nav-icon">${m.icon}</span>
                    <span class="nav-label">${m.label}</span>
                </a>
            `).join('');

        if (this.user && this.user.rol === 'ADMIN') {
            document.querySelectorAll('.telemetry-item').forEach(el => el.style.display = 'flex');
            const btnCmd = document.getElementById('btn-command');
            if (btnCmd) btnCmd.style.display = 'block';
        }
    },

    bindEvents() {
        document.getElementById('sidebar-toggle')?.addEventListener('click', (e) => {
            e.stopPropagation();
            const sidebar = document.getElementById('shell-sidebar');
            if (window.innerWidth < 1024) {
                sidebar.classList.toggle('active');
            } else {
                sidebar.classList.toggle('collapsed');
            }
        });

        document.getElementById('neural-overlay')?.addEventListener('click', () => {
            document.getElementById('shell-sidebar').classList.remove('active');
        });

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth < 1024) {
                    document.getElementById('shell-sidebar').classList.remove('active');
                }
            });
        });

        document.getElementById('btn-logout')?.addEventListener('click', () => {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
            localStorage.removeItem('auth_role');
            localStorage.removeItem('active_shift');
            window.location.href = '/static/login.html';
        });

        document.getElementById('btn-notifications')?.addEventListener('click', () => {
            this.toggleNotifications();
        });

        document.getElementById('btn-command')?.addEventListener('click', () => {
            this.toggleCommandPalette();
        });

        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') { 
                e.preventDefault(); 
                const search = document.getElementById('sidebar-module-search');
                if (search) {
                    search.focus();
                    const sidebar = document.getElementById('shell-sidebar');
                    if (sidebar.classList.contains('collapsed')) sidebar.classList.remove('collapsed');
                } else {
                    this.toggleCommandPalette();
                }
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'j') { e.preventDefault(); this.toggleNeuralMonitor(); }
            if (e.key === 'Escape') { 
                document.getElementById('command-palette')?.classList.add('hidden');
                document.getElementById('neural-monitor')?.classList.add('translate-x-full');
                document.getElementById('notification-panel')?.classList.add('hidden');
                document.getElementById('carbonito-chat')?.classList.add('hidden');
            }
        });

        document.getElementById('sidebar-module-search')?.addEventListener('input', (e) => {
            this.filterModules(e.target.value);
        });
    },

    toggleNotifications() {
        document.getElementById('notification-panel')?.classList.toggle('hidden');
    },

    async pollNotifications() {
        if (!this.user) return;
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch('/api/notifications/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                this.updateNotifications(data);
            }
        } catch (e) {
            console.error("[Shell] Polling Error:", e);
        }
        setTimeout(() => this.pollNotifications(), 15000);
    },

    updateNotifications(notifs) {
        const list = document.getElementById('notif-list');
        const badge = document.getElementById('notif-badge');
        if (!list) return;

        if (notifs.length === 0) {
            list.innerHTML = '<div class="empty-state">No hay alertas activas.</div>';
            if (badge) badge.style.display = 'none';
            return;
        }

        if (badge) {
            badge.innerText = notifs.length;
            badge.style.display = 'block';
        }

        list.innerHTML = notifs.map(n => `
            <div class="notif-item ${n.type}">
                <div class="notif-icon">${n.type === 'warning' ? '⚠️' : 'ℹ️'}</div>
                <div class="notif-content">
                    <p class="notif-title">${n.title}</p>
                    <p class="notif-msg">${n.message}</p>
                    <span class="notif-time">${new Date(n.timestamp).toLocaleTimeString()}</span>
                </div>
            </div>
        `).join('');
    },

    async pollInsights() {
        if (this.user?.rol !== 'ADMIN') return;
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch('/api/telemetry/insights', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                this.handleInsights(data);
            }
        } catch (e) {}
        setTimeout(() => this.pollInsights(), 30000); // Check every 30s
    },

    handleInsights(data) {
        if (!data.insights || data.insights.length === 0) return;
        
        // Inyectar el insight más crítico en el banner superior si es nuevo
        const topInsight = data.insights[0];
        const banner = document.getElementById('neural-load');
        if (banner) {
            const insightTag = document.createElement('div');
            insightTag.className = `insight-pill ${topInsight.level.toLowerCase()}`;
            insightTag.innerHTML = `<span>🧠</span> ${topInsight.message}`;
            
            // Reemplazar si existe
            const existing = banner.querySelector('.insight-pill');
            if (existing) existing.remove();
            banner.appendChild(insightTag);
        }

        // Actualizar el estado del sistema en la Matrix
        const health = data.system_health;
        console.log(`[Neural] Health: ${health.neural_load}% Load | ${health.database_latency} DB`);
    },

    startTelemetry() {
        setInterval(async () => {
            if (this.user?.rol !== 'ADMIN') return;
            try {
                const res = await fetch('/api/health');
                if (!res.ok) return;
                const data = await res.json();
                
                const latEl = document.getElementById('latency-val');
                if (latEl) latEl.innerText = `${data.telemetry.database.latency_ms.toFixed(1)}ms`;
                
                const cpuBar = document.getElementById('cpu-bar');
                if (cpuBar) cpuBar.style.width = `${data.telemetry.cpu_usage}%`;

                // Update neural monitor if open
                const monitor = document.getElementById('neural-monitor');
                const logsCont = document.getElementById('neural-logs');
                if (logsCont && monitor && !monitor.classList.contains('translate-x-full')) {
                    const token = localStorage.getItem('auth_token');
                    const logRes = await fetch('/api/system/telemetry/logs', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (logRes.ok) {
                        const logData = await logRes.json();
                        const allLines = Object.values(logData.logs).flat();
                        const lastLines = allLines.slice(-10); // Only last 10 for performance
                        
                        logsCont.innerHTML = lastLines.map(line => `
                            <div class="flex gap-2 text-[9px] border-l border-white/10 pl-2">
                                <span class="text-indigo-400">[SYSTEM]</span> <span>${line}</span>
                            </div>
                        `).join('');
                        logsCont.scrollTop = logsCont.scrollHeight;
                    }
                }
            } catch(e) {}
        }, 5000);
    },

    injectSystemBanner() {
        if (document.getElementById('shell-clock')) return;
        const info = document.createElement('div');
        info.className = "fixed bottom-4 right-24 z-[2000] flex items-center gap-4 text-[9px] font-mono text-slate-400 pointer-events-none select-none";
        info.innerHTML = `<span id="shell-clock">00:00:00</span> <span class="opacity-30">|</span> <span>SINGULARITY-NODE-01</span>`;
        document.body.appendChild(info);
        setInterval(() => {
            const clockEl = document.getElementById('shell-clock');
            if (clockEl) clockEl.innerText = new Date().toLocaleTimeString('es-ES', {hour12: false});
        }, 1000);
    },

    injectNeuralMonitor() {
        if (this.user?.rol !== 'ADMIN') return;
        if (document.getElementById('neural-monitor')) return;
        const monitor = document.createElement('div');
        monitor.id = 'neural-monitor';
        monitor.className = "fixed top-0 right-0 w-[400px] h-screen bg-slate-900 text-white p-8 z-[2500] transform translate-x-full transition-transform duration-500 shadow-2xl font-mono";
        monitor.innerHTML = `
            <div class="flex justify-between items-center mb-8">
                <span class="text-xs font-bold text-indigo-400">NEURAL STREAM [DECRYPTED]</span>
                <button onclick="EnterpriseShell.toggleNeuralMonitor()" class="opacity-50 hover:opacity-100">✕</button>
            </div>
            <div id="neural-logs" class="space-y-1 h-[70vh] overflow-y-auto custom-scrollbar text-[10px] opacity-70">
                <div>[INIT] Handshake with Quantum Core...</div>
            </div>
        `;
        document.body.appendChild(monitor);
    },

    toggleNeuralMonitor() {
        if (this.user?.rol !== 'ADMIN') return;
        document.getElementById('neural-monitor')?.classList.toggle('translate-x-full');
    },

    injectCommandPalette() {
        if (document.getElementById('command-palette')) return;
        const palette = document.createElement('div');
        palette.id = 'command-palette';
        palette.className = "fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[3000] hidden flex items-start justify-center pt-32";
        palette.innerHTML = `
            <div class="w-full max-w-xl bg-white rounded-3xl shadow-2xl overflow-hidden p-4">
                <input type="text" id="palette-search" placeholder="Comando rápido..." class="w-full p-6 text-xl font-bold border-none focus:ring-0">
                <div id="palette-results" class="max-h-96 overflow-y-auto p-4 space-y-2">
                    ${this.modules.map(m => `
                        <a href="javascript:void(0)" onclick="EnterpriseShell.loadModule('${m.id}'); EnterpriseShell.toggleCommandPalette()" class="flex items-center gap-4 p-4 rounded-2xl hover:bg-indigo-50 transition-colors">
                            <span>${m.icon}</span>
                            <span class="font-bold">${m.label}</span>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
        palette.onclick = (e) => { if (e.target === palette) this.toggleCommandPalette(); };
        document.body.appendChild(palette);
    },

    toggleCommandPalette() {
        const p = document.getElementById('command-palette');
        if (p) {
            p.classList.toggle('hidden');
            if (!p.classList.contains('hidden')) document.getElementById('palette-search')?.focus();
        }
    },

    injectCarbonitoUI() {
        if (document.getElementById('carbonito-launcher')) return;
        
        // Launcher
        const launcher = document.createElement('button');
        launcher.id = 'carbonito-launcher';
        launcher.className = "fixed bottom-10 right-10 w-16 h-16 rounded-3xl bg-indigo-600 text-white shadow-2xl flex items-center justify-center text-2xl hover:scale-110 transition-all z-[2000] border-4 border-white";
        launcher.innerHTML = `🤖`;
        launcher.onclick = () => this.toggleCarbonito();
        document.body.appendChild(launcher);

        // Chat Panel
        const chat = document.createElement('div');
        chat.id = 'carbonito-chat';
        chat.className = "fixed bottom-32 right-10 w-[400px] bg-white rounded-[2.5rem] shadow-[0_20px_50px_-10px_rgba(79,70,229,0.3)] border border-slate-100 z-[3000] hidden flex flex-col overflow-hidden transform transition-all duration-300 translate-y-10 opacity-0 scale-95";
        chat.innerHTML = `
            <div class="p-8 bg-indigo-600 text-white flex justify-between items-center">
                <div>
                    <h3 class="text-lg font-black tracking-tight uppercase">Carbonito AI</h3>
                    <p class="text-[10px] font-bold opacity-60 uppercase tracking-widest">Enterprise Assistant v2.0</p>
                </div>
                <button onclick="EnterpriseShell.toggleCarbonito()" class="text-2xl opacity-50 hover:opacity-100">×</button>
            </div>
            <div id="chat-messages" class="flex-1 p-6 space-y-4 overflow-y-auto max-h-[400px] custom-scrollbar bg-slate-50/50">
                <div class="message system bg-white border border-slate-100 p-4 rounded-2xl text-xs text-slate-600">
                    Hola ${this.user ? this.user.full_name : 'invitado'}, soy Carbonito. Estoy analizando el flujo de trabajo en tiempo real para asistirte.
                </div>
            </div>
            <div class="p-4 bg-white border-t border-slate-100 flex gap-2">
                <input type="text" id="chat-input" placeholder="Pregúntame algo sobre la operativa..." class="flex-1 bg-slate-50 border-none rounded-2xl p-4 text-xs font-bold focus:ring-2 focus:ring-indigo-600 transition-all">
                <button id="btn-send-chat" class="w-12 h-12 bg-indigo-600 text-white rounded-2xl flex items-center justify-center">🚀</button>
            </div>
        `;
        document.body.appendChild(chat);

        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
        document.getElementById('btn-send-chat')?.addEventListener('click', () => this.sendChatMessage());
    },

    toggleCarbonito() {
        const chat = document.getElementById('carbonito-chat');
        if (!chat) return;
        const isHidden = chat.classList.contains('hidden');
        if (isHidden) {
            chat.classList.remove('hidden');
            setTimeout(() => {
                chat.classList.remove('translate-y-10', 'opacity-0', 'scale-95');
                document.getElementById('chat-input')?.focus();
            }, 10);
        } else {
            chat.classList.add('translate-y-10', 'opacity-0', 'scale-95');
            setTimeout(() => chat.classList.add('hidden'), 300);
        }
    },

    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const text = input.value.trim();
        if (!text) return;

        const messages = document.getElementById('chat-messages');
        const userMsg = document.createElement('div');
        userMsg.className = "message user ml-12 bg-indigo-600 text-white p-4 rounded-2xl rounded-tr-none text-xs font-bold";
        userMsg.innerText = text;
        messages.appendChild(userMsg);
        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        // Artificial intelligence delay
        const typing = document.createElement('div');
        typing.className = "message ai mr-12 bg-white border border-slate-100 p-4 rounded-2xl rounded-tl-none text-xs text-slate-600 italic";
        typing.innerText = "Pensando...";
        messages.appendChild(typing);

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ 
                    message: text,
                    context: {
                        path: window.location.pathname,
                        module: document.getElementById('module-title')?.innerText || 'Unknown'
                    }
                })
            });
            const data = await response.json();
            typing.innerText = data.reply || "No puedo procesar esa solicitud en este momento.";
            typing.classList.remove('italic');
        } catch (e) {
            typing.innerText = "Error de conexión con el núcleo neural.";
        }
        messages.scrollTop = messages.scrollHeight;
    },

    injectGlobalStyles() {
        if (document.getElementById('shell-global-styles')) return;
        const s = document.createElement('style');
        s.id = 'shell-global-styles';
        s.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;900&display=swap');
            :root { --sidebar-width: 260px; }
            
            #shell-sidebar.collapsed .nav-label, #shell-sidebar.collapsed .user-info { display: none; }
            #shell-nav { flex: 1; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
            .nav-item { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: 1.25rem; text-decoration: none; color: #64748b; font-weight: 700; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); font-size: 0.85rem; }
            .nav-item:hover { background: #f1f5f9; color: #0f172a; transform: translateX(4px); }
            .nav-item.active { background: #eef2ff; color: #4f46e5; box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.1); }
            .nav-icon { font-size: 1.25rem; }
            
            .sidebar-footer { padding: 1.5rem; border-top: 1px solid #f1f5f9; }
            .user-pill { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
            .user-avatar { width: 40px; height: 40px; border-radius: 12px; background: #4f46e5; color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; }
            .user-info { display: flex; flex-direction: column; }
            .user-name { font-size: 0.8rem; font-weight: 900; color: #0f172a; }
            .user-role { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; }
            .btn-logout { width: 100%; padding: 0.85rem; border-radius: 1rem; background: #fef2f2; color: #ef4444; border: none; font-weight: 900; cursor: pointer; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.1em; transition: all 0.2s; }
            .btn-logout:hover { background: #fee2e2; transform: translateY(-1px); }
            
            #shell-topbar { height: 80px; padding: 0 1.5rem; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid #f1f5f9; position: sticky; top: 0; z-index: 900; }
            .topbar-left { display: flex; align-items: center; gap: 1.5rem; }
            #sidebar-toggle { font-size: 1.5rem; background: none; border: none; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 0.75rem; transition: all 0.2s; }
            #sidebar-toggle:hover { background: #f1f5f9; color: #0f172a; }
            #module-title { font-size: 1.25rem; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; }
            
            .topbar-right { display: flex; align-items: center; gap: 1.25rem; }
            .telemetry-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.7rem; font-weight: 900; color: #64748b; }
            .bar-container { width: 60px; height: 4px; background: #f1f5f9; border-radius: 2px; overflow: hidden; }
            .bar { height: 100%; background: #4f46e5; transition: width 1s ease; }
            .shell-icon-btn { width: 42px; height: 42px; border-radius: 12px; border: 1px solid #f1f5f9; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; position: relative; transition: all 0.2s; }
            .shell-icon-btn:hover { background: #f8fafc; transform: translateY(-1px); border-color: #e2e8f0; }
            .notif-badge { position: absolute; top: -4px; right: -4px; background: #ef4444; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; border: 2px solid white; font-weight: 900; }
            
            .shell-panel { position: fixed; top: 90px; right: 1.5rem; width: 380px; background: white; border-radius: 2rem; border: 1px solid #f1f5f9; z-index: 2000; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.1); }
            .panel-header { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em; color: #0f172a; }
            .close-panel { font-size: 1.5rem; opacity: 0.3; transition: all 0.2s; background: none; border: none; cursor: pointer; }
            .close-panel:hover { opacity: 1; }
            .panel-body { padding: 1rem; max-height: 480px; overflow-y: auto; }
            
            .notif-item { display: flex; gap: 1rem; padding: 1.25rem; border-radius: 1.25rem; margin-bottom: 0.75rem; border: 1px solid #f1f5f9; transition: all 0.2s; }
            .notif-item:hover { border-color: #e2e8f0; transform: scale(1.02); }
            .notif-item.warning { border-left: 4px solid #f59e0b; background: #fffbeb; }
            .notif-item.error { border-left: 4px solid #ef4444; background: #fef2f2; }
            .notif-icon { font-size: 1.25rem; }
            .notif-title { font-size: 0.85rem; font-weight: 900; color: #0f172a; margin-bottom: 0.25rem; }
            .notif-msg { font-size: 0.75rem; color: #64748b; font-weight: 500; line-height: 1.4; }
            .notif-time { font-size: 0.65rem; color: #94a3b8; font-weight: 700; display: block; margin-top: 0.5rem; text-transform: uppercase; }
            
            .insight-pill { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 1rem; border-radius: 2rem; font-size: 10px; font-weight: 900; animation: slideInRight 0.5s cubic-bezier(0.23, 1, 0.32, 1); max-width: 220px; text-transform: uppercase; }
            .insight-pill.critical { background: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; }
            .insight-pill.info { background: #e0f2fe; color: #0ea5e9; border: 1px solid #7dd3fc; }
            .insight-pill.success { background: #dcfce7; color: #22c55e; border: 1px solid #86efac; }
            
            #shell-breadcrumbs { display: flex; gap: 0.5rem; font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: -4px; }
            .bc-item.current { color: #4f46e5; }
            .bc-sep { opacity: 0.3; }
            
            @media (max-width: 1024px) {
                .shell-panel { right: 1rem; width: calc(100vw - 2rem); max-width: 380px; }
            }
        `;
        document.head.appendChild(s);
    }
};

document.addEventListener('DOMContentLoaded', () => EnterpriseShell.init());
window.EnterpriseShell = EnterpriseShell;
