/**
 * Carbones y Pollos - Enterprise UI Components
 * Unified Professional Components for the Quantum Singularity
 */

const EnterpriseUI = {
    /**
     * Renders a professional empty state in a container
     * @param {string} containerId - Target container ID
     * @param {Object} options - { title, message, icon, ctaLabel, ctaAction }
     */
    renderEmptyState(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            title = "Sin Datos",
            message = "No se ha encontrado información en este nodo neural.",
            icon = "📡",
            ctaLabel = "Actualizar",
            ctaAction = () => location.reload()
        } = options;

        container.innerHTML = `
            <div class="flex flex-col items-center justify-center p-20 text-center animate-in fade-in zoom-in duration-500">
                <div class="text-7xl mb-8 filter grayscale opacity-20">${icon}</div>
                <h3 class="text-2xl font-black text-slate-800 uppercase tracking-tight mb-2">${title}</h3>
                <p class="text-slate-500 max-w-sm mx-auto mb-8 text-sm leading-relaxed">${message}</p>
                <button id="empty-state-cta" class="bg-indigo-600 text-white px-8 py-3 rounded-2xl font-black uppercase text-[10px] tracking-widest shadow-xl shadow-indigo-500/20 hover:scale-105 active:scale-95 transition-all">
                    ${ctaLabel}
                </button>
            </div>
        `;

        const btn = document.getElementById('empty-state-cta');
        if (btn) btn.onclick = ctaAction;
    },

    /**
     * Shows a global loading overlay
     */
    showLoading(message = "Sincronizando con Quantum Core...") {
        if (document.getElementById('quantum-loader')) return;
        const loader = document.createElement('div');
        loader.id = 'quantum-loader';
        loader.className = "fixed inset-0 z-[9999] bg-slate-900/60 backdrop-blur-md flex flex-col items-center justify-center text-white";
        loader.innerHTML = `
            <div class="relative w-24 h-24 mb-8">
                <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-4 bg-indigo-600 rounded-full animate-pulse flex items-center justify-center text-xl">🔥</div>
            </div>
            <p class="text-[10px] font-black uppercase tracking-[0.4em] animate-pulse">${message}</p>
        `;
        document.body.appendChild(loader);
    },

    hideLoading() {
        const loader = document.getElementById('quantum-loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 300);
        }
    },

    /**
     * Standard notification toast
     */
    notify(message, type = "info") {
        const colors = {
            info: "#4f46e5",
            success: "#10b981",
            error: "#ef4444",
            warning: "#f59e0b"
        };
        
        // Simple console fallback if shell not ready
        console.log(`[UI-NOTIFY] ${type.toUpperCase()}: ${message}`);
        
        // If EnterpriseShell has a notification method, use it
        if (typeof EnterpriseShell !== 'undefined' && EnterpriseShell.updateNotifications) {
            // EnterpriseShell.updateNotifications([{ title: type.toUpperCase(), message, type, timestamp: Date.now() }]);
        }
    },

    /**
     * Renders a professional KPI Card with trend indicators
     */
    renderKPICard(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            title = "Metric",
            value = "0",
            unit = "",
            trend = "up",
            trendValue = "",
            icon = "fa-chart-line",
            color = "indigo"
        } = options;

        const trendIcon = trend === 'up' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
        const trendColor = trend === 'up' ? 'text-emerald-500' : 'text-red-500';

        const card = document.createElement('div');
        card.className = `glass-container p-6 rounded-[2rem] border-${color}-500/20 hover:scale-[1.02] transition-all duration-300`;
        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div class="flex flex-col">
                    <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">${title}</p>
                    <div class="flex items-center gap-1.5 ${trendColor} text-[8px] font-black uppercase">
                        <i class="fa-solid ${trendIcon}"></i>
                        <span>${trendValue}</span>
                    </div>
                </div>
                <div class="w-10 h-10 rounded-xl bg-${color}-500/10 flex items-center justify-center">
                    <i class="fa-solid ${icon} text-${color}-500"></i>
                </div>
            </div>
            <div class="flex items-baseline gap-2">
                <span class="text-3xl font-black tracking-tighter text-slate-900">${value}</span>
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">${unit}</span>
            </div>
        `;
        container.appendChild(card);
    },

    /**
     * Creates a professional industrial badge
     */
    createBadge(text, type = "info") {
        const types = {
            info: "bg-indigo-50 text-indigo-600 border-indigo-100",
            success: "bg-emerald-50 text-emerald-600 border-emerald-100",
            error: "bg-red-50 text-red-600 border-red-100",
            warning: "bg-amber-50 text-amber-600 border-amber-100"
        };
        return `<span class="px-3 py-1 rounded-full border ${types[type] || types.info} text-[8px] font-black uppercase tracking-widest">${text}</span>`;
    },

    /**
     * Generates a professional industrial table
     */
    createTable(headers, rows) {
        return `
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-white/5">
                            ${headers.map(h => `<th class="py-4 px-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">${h}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-white/5">
                        ${rows.map(row => `
                            <tr class="hover:bg-white/5 transition-colors">
                                ${row.map(cell => `<td class="py-4 px-6 text-sm font-medium text-slate-300">${cell}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    /**
     * Global keyboard shortcuts registry
     */
    addGlobalKeyHandler(key, callback) {
        window.addEventListener('keydown', (e) => {
            if (e.key === key) {
                e.preventDefault();
                callback();
            }
        });
    }
};

window.EnterpriseUI = EnterpriseUI;
