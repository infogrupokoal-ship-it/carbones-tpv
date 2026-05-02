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

    // 6. Inject Carbonito AI
    injectCarbonitoAI();
}

function injectSidebar(role, user) {
    const sidebarHTML = `
    <aside id="enterprise-sidebar" class="w-64 glass-panel border-r border-slate-200 flex flex-col p-6 h-screen sticky top-0 hidden md:flex">
        <div class="flex items-center gap-3 mb-10">
            <div class="h-10 w-10 bg-blue-600 rounded-xl flex items-center justify-center text-xl shadow-lg shadow-blue-900/40 text-white">⚡</div>
            <div class="flex flex-col">
                <h2 class="text-xl font-black text-slate-900 tracking-tighter uppercase leading-tight">TPV <span class="text-blue-600">Ultra</span></h2>
                <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Enterprise Edition</span>
            </div>
        </div>

        <nav class="space-y-2 flex-1 overflow-y-auto pr-2 custom-scrollbar">
            <!-- Ecosistema -->
            <div class="nav-group">
                <button class="nav-group-btn w-full flex items-center justify-between px-3 py-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-bold text-sm" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="flex items-center gap-2"><span>🌐</span> Ecosistema</div>
                    <span class="text-xs">▼</span>
                </button>
                <div class="nav-submenu hidden pl-6 pr-2 py-1 space-y-1">
                    <a href="/static/portal.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="portal.html">🏠 Portal de Inicio</a>
                    <a href="/static/dashboard.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="dashboard.html">📊 Dashboard BI</a>
                </div>
            </div>
            
            <!-- Operaciones -->
            <div class="nav-group">
                <button class="nav-group-btn w-full flex items-center justify-between px-3 py-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-bold text-sm" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="flex items-center gap-2"><span>⚡</span> Operaciones</div>
                    <span class="text-xs">▼</span>
                </button>
                <div class="nav-submenu hidden pl-6 pr-2 py-1 space-y-1">
                    <a href="/static/caja.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="caja.html">💰 Control de Caja</a>
                    <a href="/static/kds.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="kds.html">🍳 Cocina KDS</a>
                    <a href="/static/inventario.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="inventario.html">📦 Inventario Central</a>
                </div>
            </div>
            
            <!-- Crecimiento -->
            <div class="nav-group">
                <button class="nav-group-btn w-full flex items-center justify-between px-3 py-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-bold text-sm" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="flex items-center gap-2"><span>🚀</span> Crecimiento</div>
                    <span class="text-xs">▼</span>
                </button>
                <div class="nav-submenu hidden pl-6 pr-2 py-1 space-y-1">
                    <a href="/static/presupuestos.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="presupuestos.html">📄 Presupuestos</a>
                    <a href="/static/referidos.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="referidos.html">🔗 Referidos</a>
                    <a href="/static/marketing.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="marketing.html">📣 Marketing Hub</a>
                </div>
            </div>

            <!-- Gestión -->
            <div class="nav-group">
                <button class="nav-group-btn w-full flex items-center justify-between px-3 py-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-bold text-sm" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="flex items-center gap-2"><span>⚙️</span> Gestión</div>
                    <span class="text-xs">▼</span>
                </button>
                <div class="nav-submenu hidden pl-6 pr-2 py-1 space-y-1">
                    <a href="/static/rrhh.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="rrhh.html">👥 RRHH & Personal</a>
                    <a href="/static/liquidaciones.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="liquidaciones.html">💰 Liquidaciones</a>
                    <a href="/static/repartidores.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="repartidores.html">🛵 Repartidores</a>
                    <a href="/static/stats.html" class="nav-link block px-3 py-2 text-sm text-slate-500 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg" data-path="stats.html">📈 Analytics Pro</a>
                </div>
            </div>
        </nav>

        <div class="mt-auto pt-6 border-t border-slate-200">
            <div class="flex items-center gap-3 p-3 bg-slate-100 rounded-2xl mb-4">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs border border-blue-200">👤</div>
                <div class="flex flex-col">
                    <span class="text-[10px] font-black text-slate-900 uppercase truncate w-32">${user || 'Admin'}</span>
                    <span class="text-[8px] font-bold text-slate-500 uppercase tracking-widest">${role === 'admin' ? 'Super Admin' : 'Staff'}</span>
                </div>
            </div>
            <button onclick="logoutShell()" class="w-full p-3 rounded-xl hover:bg-red-500/10 text-red-500 text-[10px] font-black uppercase tracking-widest transition-all border border-transparent hover:border-red-500/20">Cerrar Sesión</button>
        </div>
    </aside>

    <!-- Mobile Header -->
    <header class="md:hidden fixed top-0 w-full glass-panel z-50 p-4 flex justify-between items-center border-b border-slate-200">
        <h2 class="text-lg font-black text-slate-900 tracking-tighter uppercase">TPV <span class="text-blue-600">Ultra</span></h2>
        <button id="mobile-toggle" class="p-2 bg-slate-100 rounded-lg text-slate-900">☰</button>
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
            <a href="/static/portal.html" class="breadcrumb-item hover:text-slate-900 transition-colors">Enterprise</a>
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

function injectCarbonitoAI() {
    const aiHTML = `
    <!-- Carbonito AI Floating Button -->
    <button id="carbonito-fab" onclick="toggleCarbonito()" class="fixed bottom-6 left-6 z-[90] w-14 h-14 bg-gradient-to-tr from-emerald-600 to-emerald-400 rounded-full shadow-2xl shadow-emerald-900/50 flex items-center justify-center text-2xl hover:scale-110 transition-transform cursor-pointer border border-white/20">
        🔥
        <span class="absolute -top-1 -right-1 flex h-4 w-4">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border border-slate-900"></span>
        </span>
    </button>

    <!-- Carbonito AI Panel -->
    <div id="carbonito-panel" class="fixed bottom-24 left-6 z-[90] w-80 md:w-96 h-[500px] max-h-[70vh] bg-white/95 backdrop-blur-xl border border-slate-200 rounded-3xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 transform scale-95 opacity-0 pointer-events-none origin-bottom-left">
        <!-- Header -->
        <div class="p-4 border-b border-slate-200 flex justify-between items-center bg-gradient-to-r from-emerald-50 to-transparent">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-xl">🔥</div>
                <div>
                    <h3 class="text-slate-900 font-black uppercase tracking-tighter text-sm">Carbonito AI</h3>
                    <p class="text-[9px] text-emerald-600 uppercase tracking-widest font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span> Online</p>
                </div>
            </div>
            <button onclick="toggleCarbonito()" class="text-slate-400 hover:text-slate-900 p-2 text-xl">&times;</button>
        </div>

        <!-- Chat History -->
        <div id="carbonito-history" class="flex-1 p-4 overflow-y-auto flex flex-col gap-4 custom-scrollbar">
            <div class="flex gap-3 max-w-[85%]">
                <div class="w-8 h-8 rounded-full bg-emerald-100 flex-shrink-0 flex items-center justify-center text-sm">🔥</div>
                <div class="bg-slate-100 p-3 rounded-2xl rounded-tl-none border border-slate-200">
                    <p class="text-sm text-slate-700">¡Hola! Soy Carbonito, tu asistente inteligente. ¿En qué te puedo ayudar hoy con el sistema?</p>
                </div>
            </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-slate-200 bg-slate-50">
            <form id="carbonito-form" onsubmit="sendCarbonitoMessage(event)" class="relative">
                <input type="text" id="carbonito-input" placeholder="Pregunta algo..." class="w-full bg-white border border-slate-300 rounded-xl py-3 pl-4 pr-12 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 transition-colors shadow-sm">
                <button type="submit" class="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
                    <svg class="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
                </button>
            </form>
        </div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', aiHTML);
}

window.toggleCarbonito = function() {
    const panel = document.getElementById('carbonito-panel');
    if (panel.classList.contains('opacity-0')) {
        panel.classList.remove('opacity-0', 'scale-95', 'pointer-events-none');
        panel.classList.add('opacity-100', 'scale-100', 'pointer-events-auto');
        document.getElementById('carbonito-input').focus();
    } else {
        panel.classList.add('opacity-0', 'scale-95', 'pointer-events-none');
        panel.classList.remove('opacity-100', 'scale-100', 'pointer-events-auto');
    }
};

window.sendCarbonitoMessage = async function(e) {
    e.preventDefault();
    const input = document.getElementById('carbonito-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    const history = document.getElementById('carbonito-history');

    // Add user message
    history.insertAdjacentHTML('beforeend', \`
        <div class="flex gap-3 max-w-[85%] self-end flex-row-reverse">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center text-sm">👤</div>
            <div class="bg-blue-600 p-3 rounded-2xl rounded-tr-none shadow-sm">
                <p class="text-sm text-white">\${msg}</p>
            </div>
        </div>
    \`);
    history.scrollTop = history.scrollHeight;

    // Loading state
    const loadingId = 'loading-' + Date.now();
    history.insertAdjacentHTML('beforeend', \`
        <div id="\${loadingId}" class="flex gap-3 max-w-[85%]">
            <div class="w-8 h-8 rounded-full bg-emerald-100 flex-shrink-0 flex items-center justify-center text-sm animate-pulse">🔥</div>
            <div class="bg-slate-100 p-3 rounded-2xl rounded-tl-none border border-slate-200 flex items-center gap-1">
                <span class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                <span class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                <span class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            </div>
        </div>
    \`);
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: msg, context: 'El usuario está en el portal Enterprise Staff.' })
        });
        const data = await response.json();

        document.getElementById(loadingId).remove();

        history.insertAdjacentHTML('beforeend', \`
            <div class="flex gap-3 max-w-[85%]">
                <div class="w-8 h-8 rounded-full bg-emerald-100 flex-shrink-0 flex items-center justify-center text-sm">🔥</div>
                <div class="bg-slate-100 p-3 rounded-2xl rounded-tl-none border border-slate-200">
                    <p class="text-sm text-slate-700">\${data.reply || 'Ha ocurrido un error.'}</p>
                </div>
            </div>
        \`);
    } catch (err) {
        document.getElementById(loadingId).remove();
        history.insertAdjacentHTML('beforeend', \`
            <div class="flex gap-3 max-w-[85%]">
                <div class="w-8 h-8 rounded-full bg-red-100 flex-shrink-0 flex items-center justify-center text-sm">⚠️</div>
                <div class="bg-red-50 p-3 rounded-2xl rounded-tl-none border border-red-200">
                    <p class="text-sm text-red-600">Error de conexión con Carbonito.</p>
                </div>
            </div>
        \`);
    }
    history.scrollTop = history.scrollHeight;
};

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
        toast.className = 'toast page-fade-in pointer-events-auto flex items-center gap-3 p-4 bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-xl text-slate-900 min-w-[280px]';
        
        let iconHtml;
        if (type === 'error') {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-lg">⚠️</div>`;
        } else if (type === 'success') {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 text-lg">✅</div>`;
        } else {
            iconHtml = `<div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-lg">ℹ️</div>`;
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
