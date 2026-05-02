/**
 * ENTERPRISE SHELL ENGINE v4.1
 * Unified Management for TPV Suite
 */

document.addEventListener('DOMContentLoaded', () => {
    initShell();
});

function initShell() {
    // 1. Auth Check
    const role = localStorage.getItem('auth_role');
    const user = localStorage.getItem('auth_user');
    if (!role && !window.location.pathname.includes('login.html')) {
        window.location.href = '/static/login.html';
        return;
    }

    // 2. Inject Sidebar if missing
    if (!document.getElementById('enterprise-sidebar')) {
        injectSidebar(role, user);
    }

    // 3. Highlight Active Link
    highlightActiveLink();

    // 4. Inject Breadcrumbs
    injectBreadcrumbs();

    // 5. Setup Mobile Toggle
    setupMobileToggle();
}

function injectSidebar(role, user) {
    const sidebarHTML = `
    <aside id="enterprise-sidebar" class="w-72 glass-panel border-r border-white/5 flex flex-col p-6 h-screen sticky top-0 hidden lg:flex">
        <div class="flex items-center gap-3 mb-10">
            <div class="h-10 w-10 bg-blue-600 rounded-xl flex items-center justify-center text-xl shadow-lg shadow-blue-900/40">⚡</div>
            <div class="flex flex-col">
                <h2 class="text-xl font-black text-white tracking-tighter uppercase leading-tight">TPV <span class="text-blue-500">Ultra</span></h2>
                <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Enterprise Edition</span>
            </div>
        </div>

        <nav class="space-y-1 flex-1 overflow-y-auto pr-2 custom-scrollbar">
            <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 mt-4 px-3">Ecosistema</p>
            <a href="/static/portal.html" class="nav-link" data-path="portal.html"><span>🏠</span> Portal de Inicio</a>
            <a href="/static/dashboard.html" class="nav-link" data-path="dashboard.html"><span>📊</span> Dashboard BI</a>
            
            <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 mt-6 px-3">Operaciones</p>
            <a href="/static/caja.html" class="nav-link" data-path="caja.html"><span>💰</span> Control de Caja</a>
            <a href="/static/kds.html" class="nav-link" data-path="kds.html"><span>🍳</span> Cocina KDS</a>
            <a href="/static/inventario.html" class="nav-link" data-path="inventario.html"><span>📦</span> Inventario Central</a>
            
            <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 mt-6 px-3">Crecimiento</p>
            <a href="/static/presupuestos.html" class="nav-link" data-path="presupuestos.html"><span>📄</span> Presupuestos</a>
            <a href="/static/referidos.html" class="nav-link" data-path="referidos.html"><span>🔗</span> Referidos</a>
            <a href="/static/marketing.html" class="nav-link" data-path="marketing.html"><span>📣</span> Marketing Hub</a>

            <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 mt-6 px-3">Gestión</p>
            <a href="/static/rrhh.html" class="nav-link" data-path="rrhh.html"><span>👥</span> RRHH & Personal</a>
            <a href="/static/repartidores.html" class="nav-link" data-path="repartidores.html"><span>🛵</span> Repartidores</a>
            <a href="/static/stats.html" class="nav-link" data-path="stats.html"><span>📈</span> Analytics Pro</a>
        </nav>

        <div class="mt-auto pt-6 border-t border-white/5">
            <div class="flex items-center gap-3 p-3 bg-white/5 rounded-2xl mb-4">
                <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-xs border border-blue-500/20">👤</div>
                <div class="flex flex-col">
                    <span class="text-[10px] font-black text-white uppercase truncate w-32">${user || 'Admin'}</span>
                    <span class="text-[8px] font-bold text-slate-500 uppercase tracking-widest">${role === 'admin' ? 'Super Admin' : 'Staff'}</span>
                </div>
            </div>
            <button onclick="logoutShell()" class="w-full p-3 rounded-xl hover:bg-red-500/10 text-red-500 text-[10px] font-black uppercase tracking-widest transition-all border border-transparent hover:border-red-500/20">Cerrar Sesión</button>
        </div>
    </aside>

    <!-- Mobile Header -->
    <header class="lg:hidden fixed top-0 w-full glass-panel z-50 p-4 flex justify-between items-center border-b border-white/5">
        <h2 class="text-lg font-black text-white tracking-tighter uppercase">TPV <span class="text-blue-500">Ultra</span></h2>
        <button id="mobile-toggle" class="p-2 bg-white/5 rounded-lg text-white">☰</button>
    </header>
    `;

    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
}

function highlightActiveLink() {
    const currentPath = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('data-path') === currentPath) {
            link.classList.add('active');
        }
    });
}

function injectBreadcrumbs() {
    const main = document.querySelector('main');
    if (!main) return;

    const currentPath = window.location.pathname.split('/').pop().replace('.html', '');
    const breadcrumbHTML = `
        <div class="flex items-center gap-2 mb-8 page-fade-in">
            <a href="/static/portal.html" class="breadcrumb-item hover:text-white transition-colors">Enterprise</a>
            <span class="text-slate-700">/</span>
            <span class="breadcrumb-item text-blue-500">${currentPath}</span>
        </div>
    `;
    main.insertAdjacentHTML('afterbegin', breadcrumbHTML);
}

function setupMobileToggle() {
    const btn = document.getElementById('mobile-toggle');
    const sidebar = document.getElementById('enterprise-sidebar');
    if (btn && sidebar) {
        btn.onclick = () => {
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('flex');
            sidebar.classList.toggle('open');
        };
    }
}

function logoutShell() {
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_role');
    window.location.href = '/static/login.html';
}

window.EnterpriseShell = {
    init: (pageName) => {
        // Already handled by initShell logic but exposed for explicit calls
    },
    showEmptyState: (containerId, message, ctaText, ctaAction) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="empty-state page-fade-in">
                <div class="text-4xl mb-4 opacity-50">📂</div>
                <p class="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-6">${message}</p>
                <button onclick="${ctaAction}" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all shadow-lg shadow-blue-900/40">
                    ${ctaText}
                </button>
            </div>
        `;
    },
    showToast: (title, message, type = 'info') => {
        let container = document.getElementById('enterprise-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'enterprise-toast-container';
            container.className = 'fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = 'toast page-fade-in pointer-events-auto flex items-center gap-3 p-4 bg-slate-900/95 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl text-white min-w-[280px]';
        
        let iconHtml;
        if (type === 'error') {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-500 text-lg">⚠️</div>`;
        } else if (type === 'success') {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500 text-lg">✅</div>`;
        } else {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-500 text-lg">ℹ️</div>`;
        }

        toast.innerHTML = `
            ${iconHtml}
            <div class="flex flex-col">
                <span class="text-[10px] font-black uppercase tracking-tighter">${title}</span>
                <span class="text-[9px] font-medium text-slate-400">${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
};
