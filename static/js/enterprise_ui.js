/**
 * Carbones y Pollos - Quantum Glass UI Engine v5.0 (Industrial Singularity)
 * Superior High-Performance Components with Frosted Aesthetics & SVG Micro-Interactions.
 */

const QuantumUI = {
    version: "5.0.0-QUANTUM",
    
    injectQuantumStyles() {
        if (document.getElementById('quantum-styles')) return;
        const style = document.createElement('style');
        style.id = 'quantum-styles';
        style.textContent = `
            :root {
                --q-primary: #6366f1;
                --q-secondary: #10b981;
                --q-accent: #f59e0b;
                --q-glass: rgba(255, 255, 255, 0.7);
                --q-border: rgba(255, 255, 255, 0.4);
                --q-shadow: 0 20px 50px -12px rgba(0, 0, 0, 0.1);
                --q-font: 'Outfit', sans-serif;
            }
            .quantum-glass {
                background: var(--q-glass);
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                border: 1px solid var(--q-border);
                box-shadow: var(--q-shadow);
            }
            .quantum-card {
                transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
                border-radius: 3.5rem;
                overflow: hidden;
                position: relative;
            }
            .quantum-card:hover {
                transform: translateY(-12px) scale(1.01);
                box-shadow: 0 40px 80px -20px rgba(99, 102, 241, 0.15);
                border-color: var(--q-primary);
                background: rgba(255, 255, 255, 0.85);
            }
            .quantum-shimmer {
                position: absolute;
                top: 0; left: -100%; width: 50%; height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                transform: skewX(-20deg);
                transition: 0.75s;
            }
            .quantum-card:hover .quantum-shimmer { left: 150%; }
            
            @keyframes quantum-float {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            .animate-float { animation: quantum-float 4s ease-in-out infinite; }
            
            .text-quantum {
                background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
        `;
        document.head.appendChild(style);
    },

    renderKPICard(containerId, { title, value, unit, trend, trendValue, icon }) {
        const container = document.getElementById(containerId);
        if (!container) return;
        this.injectQuantumStyles();
        
        const trendColor = trend === 'up' ? 'text-emerald-500' : 'text-rose-500';
        const trendBg = trend === 'up' ? 'bg-emerald-50' : 'bg-rose-50';

        const card = document.createElement('div');
        card.className = "quantum-glass p-10 quantum-card group cursor-pointer";
        card.innerHTML = `
            <div class="quantum-shimmer"></div>
            <div class="flex items-start justify-between mb-8">
                <div class="w-16 h-16 rounded-[1.5rem] bg-indigo-50 flex items-center justify-center text-2xl text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-500 shadow-inner">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="flex items-center gap-2 px-4 py-1.5 rounded-full ${trendBg} ${trendColor} text-[10px] font-black uppercase tracking-widest border border-current opacity-70">
                    <i class="fas fa-arrow-${trend === 'up' ? 'up' : 'down'}"></i>
                    ${trendValue}
                </div>
            </div>
            <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-2">${title}</h3>
            <div class="flex items-baseline gap-3">
                <span class="text-5xl font-black text-quantum tracking-tighter">${value}</span>
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">${unit}</span>
            </div>
            <div class="mt-8 pt-8 border-t border-slate-100 flex items-center justify-between">
                <span class="text-[9px] font-black text-slate-300 uppercase tracking-[0.2em]">Quantum Telemetry Active</span>
                <div class="flex gap-1">
                    <div class="w-1 h-1 rounded-full bg-emerald-400 animate-pulse"></div>
                    <div class="w-1 h-1 rounded-full bg-emerald-400 opacity-50"></div>
                </div>
            </div>
        `;
        container.appendChild(card);
    },

    renderTable(containerId, { title, headers, rows }) {
        const container = document.getElementById(containerId);
        if (!container) return;
        this.injectQuantumStyles();

        let headersHtml = headers.map(h => `<th class="py-6 px-10 text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] text-left">${h}</th>`).join('');
        let rowsHtml = rows.map(row => `
            <tr class="border-t border-slate-50 hover:bg-slate-50/80 transition-all duration-300 group">
                ${row.map(cell => `<td class="py-7 px-10 text-xs font-bold text-slate-600 group-hover:text-slate-900">${cell}</td>`).join('')}
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="quantum-glass rounded-[4rem] overflow-hidden group">
                <div class="p-12 border-b border-slate-100 flex items-center justify-between">
                    <div>
                        <h3 class="text-lg font-black text-quantum tracking-tight uppercase">${title}</h3>
                        <p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.3em] mt-1">Industrial Data Grid v5.0</p>
                    </div>
                    <div class="flex gap-4">
                        <button class="bg-white border border-slate-100 p-4 rounded-2xl shadow-sm text-slate-400 hover:text-indigo-600 transition-all">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="bg-indigo-600 text-white px-8 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-indigo-100 hover:scale-105 active:scale-95 transition-all">
                            Operaciones Masivas
                        </button>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead><tr class="bg-slate-50/30">${headersHtml}</tr></thead>
                        <tbody class="divide-y divide-slate-50">${rowsHtml}</tbody>
                    </table>
                </div>
            </div>
        `;
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const config = {
            info: { bg: 'bg-indigo-600', icon: 'fa-info-circle' },
            success: { bg: 'bg-emerald-600', icon: 'fa-check-circle' },
            warning: { bg: 'bg-amber-500', icon: 'fa-exclamation-triangle' },
            error: { bg: 'bg-rose-600', icon: 'fa-times-circle' }
        };
        
        const c = config[type];
        toast.className = `fixed bottom-12 left-1/2 -translate-x-1/2 ${c.bg} text-white px-10 py-5 rounded-[2rem] font-black text-[10px] uppercase tracking-[0.2em] shadow-[0_30px_60px_-15px_rgba(0,0,0,0.3)] z-[9999] flex items-center gap-4 animate-quantum`;
        toast.innerHTML = `<i class="fas ${c.icon} text-lg"></i> ${message}`;
        
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.transition = 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
            toast.style.opacity = '0';
            toast.style.transform = 'translate(-50%, 40px) scale(0.9)';
            setTimeout(() => toast.remove(), 800);
        }, 4000);
    }
};

window.EnterpriseUI = QuantumUI;
