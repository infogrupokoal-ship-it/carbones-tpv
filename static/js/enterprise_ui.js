/**
 * Enterprise Singularity UI Engine [V9.3]
 * Librería de componentes de alta fidelidad para el ecosistema TPV.
 */
const EnterpriseUI = {
    /**
     * Renderiza una tarjeta de KPI con estética Quantum.
     */
    renderKPICard(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const card = document.createElement('div');
        card.className = 'glass-panel p-6 rounded-3xl border border-white/10 shadow-xl flex flex-col gap-4 animate-fade-in';
        
        const trendClass = data.trend === 'up' ? 'text-emerald-500' : 'text-rose-500';
        const trendIcon = data.trend === 'up' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';

        card.innerHTML = `
            <div class="flex justify-between items-center">
                <div class="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                    <i class="fas ${data.icon || 'fa-chart-line'}"></i>
                </div>
                <div class="flex items-center gap-1 ${trendClass} text-[10px] font-black uppercase tracking-tighter">
                    <i class="fas ${trendIcon}"></i> ${data.trendValue || '0%'}
                </div>
            </div>
            <div>
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">${data.title}</p>
                <div class="flex items-baseline gap-1">
                    <h3 class="text-2xl font-black text-slate-900 tracking-tighter">${data.value}</h3>
                    <span class="text-[10px] font-bold text-slate-400 uppercase">${data.unit || ''}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    },

    /**
     * Sistema de Notificaciones Globales (Quantum Toast Stack)
     */
    notify(message, type = 'info') {
        const container = document.getElementById('quantum-toast-container') || this.createToastContainer();
        const toast = document.createElement('div');
        const colors = {
            info: 'bg-indigo-600/90',
            success: 'bg-emerald-600/90',
            error: 'bg-rose-600/90',
            warning: 'bg-amber-500/90'
        };
        const icons = {
            info: 'fa-info-circle',
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle'
        };

        toast.className = `flex items-center gap-4 ${colors[type]} backdrop-blur-xl text-white px-8 py-5 rounded-[2rem] shadow-2xl border border-white/10 font-black text-[10px] uppercase tracking-widest animate-in mb-4 min-w-[300px]`;
        toast.innerHTML = `
            <i class="fas ${icons[type]} text-lg"></i>
            <div class="flex-1">${message}</div>
            <button onclick="this.parentElement.remove()" class="opacity-50 hover:opacity-100 transition-opacity">✕</button>
        `;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'quantum-toast-container';
        container.className = 'fixed bottom-10 right-10 z-[10000] flex flex-col items-end';
        document.body.appendChild(container);
        return container;
    },

    /**
     * Pantalla de Carga Industrial (Quantum Overlay)
     */
    showLoading(message = "Synchronizing Matrix...") {
        let overlay = document.getElementById('quantum-loader');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'quantum-loader';
            overlay.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-2xl z-[11000] flex flex-col items-center justify-center transition-all duration-500 opacity-0';
            overlay.innerHTML = `
                <div class="w-32 h-32 relative flex items-center justify-center">
                    <div class="absolute inset-0 border-4 border-indigo-600/20 rounded-[3rem] animate-pulse"></div>
                    <div class="absolute inset-2 border-4 border-indigo-600 rounded-[2.5rem] animate-spin [animation-duration:3s]"></div>
                    <div class="text-3xl">⚡</div>
                </div>
                <p id="loader-msg" class="mt-10 text-[10px] font-black text-white uppercase tracking-[0.6em] animate-pulse">${message}</p>
            `;
            document.body.appendChild(overlay);
        } else {
            document.getElementById('loader-msg').innerText = message;
        }
        setTimeout(() => overlay.style.opacity = '1', 10);
    },

    hideLoading() {
        const overlay = document.getElementById('quantum-loader');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 500);
        }
    },

    /**
     * Formatea moneda para el TPV
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
    },

    /**
     * Renderiza un estado vacío con estética premium (Singularity).
     */
    renderEmptyState(containerId, { title, message, icon, actionLabel, actionOnClick }) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="flex flex-col items-center justify-center p-12 text-center animate-fade-in max-w-md mx-auto">
                <div class="w-24 h-24 rounded-[2.5rem] bg-indigo-50 flex items-center justify-center text-3xl mb-8 shadow-inner border border-white">
                    <i class="fas ${icon || 'fa-box-open'} text-indigo-300"></i>
                </div>
                <h2 class="text-xl font-900 text-slate-900 tracking-tight mb-3 uppercase">${title || 'Sin Datos Disponibles'}</h2>
                <p class="text-sm font-500 text-slate-400 leading-relaxed mb-8">${message || 'Parece que no hay registros en esta sección todavía.'}</p>
                ${actionLabel ? `
                    <button onclick="${actionOnClick}" class="px-8 py-4 bg-indigo-600 text-white rounded-2xl font-800 text-[10px] uppercase tracking-widest shadow-xl shadow-indigo-500/20 hover:scale-105 active:scale-95 transition-all">
                        ${actionLabel}
                    </button>
                ` : ''}
            </div>
        `;
    }
};

window.EnterpriseUI = EnterpriseUI;
console.log("Quantum UI Engine [V9.3] Loaded Successfully.");
