/**
 * Enterprise Shell JS v2.0
 * Centralized Industrial Orchestrator for Carbones y Pollos TPV
 */

const EnterpriseShell = {
    modules: [
        { id: 'portal', label: 'Hub Principal', icon: 'grid-view', path: '/portal.html' },
        { id: 'caja', label: 'Terminal Caja', icon: 'point-of-sale', path: '/caja.html' },
        { id: 'kds', label: 'KDS Cocina', icon: 'restaurant', path: '/static/kds.html' },
        { id: 'fleet', label: 'Logística & Flota', icon: 'local-shipping', path: '/static/fleet_map.html' },
        { id: 'inventario', label: 'Inventario Pro', icon: 'inventory-2', path: '/inventario.html' },
        { id: 'dashboard', label: 'BI & Analítica', icon: 'analytics', path: '/dashboard.html' },
        { id: 'marketing', label: 'Marketing Engine', icon: 'campaign', path: '/marketing.html' },
        { id: 'analytics', label: 'Master Analytics', icon: 'monitoring', path: '/analytics.html' },
        { id: 'liquidaciones', label: 'Liquidaciones', icon: 'payments', path: '/static/liquidaciones.html' },
        { id: 'ajustes', label: 'Infraestructura', icon: 'settings', path: '/settings.html' }
    ],

    init(currentPageTitle) {
        console.log(`[Enterprise Shell] Initializing module: ${currentPageTitle}`);
        this.injectSidebar(currentPageTitle);
        this.applyBaseAnimations();
        this.setupNotificationSystem();
        this.checkAuth();
    },

    injectSidebar(activeTitle) {
        const sidebarContainer = document.getElementById('enterprise-sidebar');
        if (!sidebarContainer) return;

        const currentPath = window.location.pathname;

        let html = `
            <div class="flex flex-col h-full py-8">
                <div class="px-8 mb-12">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-200 flex items-center justify-center">
                            <span class="text-white font-black text-xs">CP</span>
                        </div>
                        <p class="font-black text-xs uppercase tracking-widest text-slate-900">Enterprise <span class="text-slate-400">v2.0</span></p>
                    </div>
                    <p class="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em]">Industrial Light Mode</p>
                </div>

                <nav class="flex-1 space-y-1">
        `;

        this.modules.forEach(m => {
            const isActive = currentPath.includes(m.path) || activeTitle === m.label;
            html += `
                <a href="${m.path}" class="nav-link ${isActive ? 'active' : ''}">
                    <span class="material-symbols-outlined text-[18px]">${m.icon}</span>
                    <span>${m.label}</span>
                </a>
            `;
        });

        html += `
                </nav>

                <div class="px-6 mt-10">
                    <div class="p-6 bg-slate-50 rounded-[2rem] border border-slate-100">
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <p class="text-[10px] font-black text-slate-900 uppercase tracking-widest">NODO ACTIVO</p>
                        </div>
                        <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mb-4">Sincronización en tiempo real activa.</p>
                        <button onclick="location.href='/logout'" class="w-full py-3 bg-white border border-slate-200 rounded-xl font-black text-[9px] uppercase tracking-widest text-slate-600 hover:bg-slate-100 transition-all">
                            Desconectar
                        </button>
                    </div>
                </div>
            </div>
        `;

        sidebarContainer.innerHTML = html;
        // Inject Material Symbols if missing
        if (!document.getElementById('material-symbols-link')) {
            const link = document.createElement('link');
            link.id = 'material-symbols-link';
            link.rel = 'stylesheet';
            link.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
            document.head.appendChild(link);
        }
    },

    applyBaseAnimations() {
        const main = document.querySelector('main');
        if (main) main.classList.add('animate-slide-up');
    },

    setupNotificationSystem() {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-10 right-10 z-[5000] flex flex-col gap-4';
        document.body.appendChild(toastContainer);

        window.showToast = (title, msg, type = 'indigo') => {
            const toast = document.createElement('div');
            const colors = {
                indigo: 'border-indigo-500 bg-white',
                emerald: 'border-emerald-500 bg-white',
                rose: 'border-rose-500 bg-white',
                amber: 'border-amber-500 bg-white'
            };
            
            toast.className = `glass-panel p-6 rounded-2xl border-l-4 ${colors[type]} shadow-2xl flex items-center gap-4 animate-slide-up min-w-[320px]`;
            toast.innerHTML = `
                <div class="flex-1">
                    <p class="text-[10px] font-black text-slate-900 uppercase tracking-widest mb-1">${title}</p>
                    <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">${msg}</p>
                </div>
            `;
            toastContainer.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        };
    },

    checkAuth() {
        // Placeholder para lógica de sesión centralizada
        const user = JSON.parse(localStorage.getItem('tpv_user') || '{}');
        if (!user.token && !window.location.pathname.includes('login.html')) {
            console.warn('[Enterprise Shell] Session lost. Redirecting to auth...');
            // window.location.href = '/static/login.html';
        }
    }
};

// Auto-init breadcrumbs if container exists
document.addEventListener('DOMContentLoaded', () => {
    const breadContainer = document.getElementById('breadcrumbs');
    if (breadContainer) {
        const path = window.location.pathname.split('/').pop().replace('.html', '');
        breadContainer.innerHTML = `
            <div class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
                <span class="hover:text-indigo-600 cursor-pointer">Enterprise</span>
                <span class="text-slate-200">/</span>
                <span class="text-slate-900">${path || 'Dashboard'}</span>
            </div>
        `;
    }
});
