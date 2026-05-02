/**
 * Carbones y Pollos - Enterprise UI Engine v1.0
 * Standardized High-Performance Components for Industrial Modules
 */

const EnterpriseUI = {
    /**
     * Renderiza una tarjeta de KPI con estilo industrial
     */
    renderKPICard(containerId, { title, value, unit, trend, trendValue, icon }) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const trendColor = trend === 'up' ? 'text-emerald-500' : 'text-rose-500';
        const trendIcon = trend === 'up' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';

        container.innerHTML += `
            <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-500 group animate-in">
                <div class="flex items-start justify-between mb-6">
                    <div class="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-2xl group-hover:bg-indigo-600 group-hover:text-white transition-all duration-500">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 ${trendColor} text-[10px] font-black uppercase tracking-widest">
                        <i class="fas ${trendIcon}"></i>
                        ${trendValue}
                    </div>
                </div>
                <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">${title}</h3>
                <div class="flex items-baseline gap-2">
                    <span class="text-3xl font-black text-slate-900 tracking-tighter">${value}</span>
                    <span class="text-xs font-bold text-slate-400 uppercase">${unit}</span>
                </div>
            </div>
        `;
    },

    /**
     * Renderiza una tabla industrial avanzada
     */
    renderTable(containerId, { title, headers, rows }) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let headersHtml = headers.map(h => `<th class="text-left py-6 px-8 text-[10px] font-black text-slate-400 uppercase tracking-widest">${h}</th>`).join('');
        let rowsHtml = rows.map(row => `
            <tr class="border-t border-slate-50 hover:bg-slate-50/50 transition-colors group">
                ${row.map(cell => `
                    <td class="py-6 px-8 text-xs font-bold text-slate-600">
                        ${cell}
                    </td>
                `).join('')}
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="bg-white rounded-[3rem] border border-slate-100 shadow-sm overflow-hidden animate-in">
                <div class="p-10 border-b border-slate-50 flex items-center justify-between">
                    <h3 class="text-sm font-black text-slate-900 uppercase tracking-tight">${title}</h3>
                    <div class="flex gap-2">
                        <button class="px-6 py-2 rounded-xl bg-slate-50 text-[10px] font-black text-slate-400 uppercase hover:bg-slate-100 transition-all">Exportar</button>
                        <button class="px-6 py-2 rounded-xl bg-indigo-600 text-[10px] font-black text-white uppercase shadow-lg shadow-indigo-100 hover:scale-105 transition-all">Acción Masiva</button>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead><tr class="bg-slate-50/30">${headersHtml}</tr></thead>
                        <tbody>${rowsHtml}</tbody>
                    </table>
                </div>
            </div>
        `;
    },

    /**
     * Inyecta una gráfica (requiere Chart.js)
     */
    renderChart(containerId, { type, labels, datasets, title }) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const canvasId = `chart-${Math.random().toString(36).substr(2, 9)}`;
        container.innerHTML = `
            <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm animate-in">
                <h3 class="text-sm font-black text-slate-900 uppercase tracking-tight mb-8">${title}</h3>
                <canvas id="${canvasId}"></canvas>
            </div>
        `;

        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded. Load it before using EnterpriseUI.renderChart');
            return;
        }

        new Chart(document.getElementById(canvasId), {
            type: type,
            data: {
                labels: labels,
                datasets: datasets.map(ds => ({
                    ...ds,
                    tension: 0.4,
                    borderRadius: 10,
                    borderWidth: 3,
                    borderColor: ds.borderColor || '#4f46e5',
                    backgroundColor: ds.backgroundColor || 'rgba(79, 70, 229, 0.1)',
                }))
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { grid: { display: false }, border: { display: false } },
                    x: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    },

    /**
     * Muestra una notificación Toast
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            info: 'bg-indigo-600',
            success: 'bg-emerald-500',
            warning: 'bg-amber-500',
            error: 'bg-rose-600'
        };
        
        toast.className = `fixed bottom-10 left-1/2 -translate-x-1/2 ${colors[type]} text-white px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-2xl z-[5000] animate-in`;
        toast.innerText = message;
        
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translate(-50%, 20px)';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }
};

window.EnterpriseUI = EnterpriseUI;
