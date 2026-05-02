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
     * Sistema de Notificaciones Globales
     */
    notify(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            info: 'bg-indigo-600',
            success: 'bg-emerald-600',
            error: 'bg-rose-600',
            warning: 'bg-amber-500'
        };

        toast.className = `fixed bottom-10 right-10 ${colors[type]} text-white px-8 py-4 rounded-2xl shadow-2xl font-black text-[10px] uppercase tracking-widest z-[9999] animate-bounce-in`;
        toast.innerHTML = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    },

    /**
     * Formatea moneda para el TPV
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
    }
};

window.EnterpriseUI = EnterpriseUI;
console.log("Quantum UI Engine [V9.3] Loaded Successfully.");
