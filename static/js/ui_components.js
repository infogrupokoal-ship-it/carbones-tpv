/**
 * Carbones y Pollos - Enterprise UI Components
 * Unified Professional Components for the Quantum Singularity
 */

const EnterpriseUI = {
    /**
     * Helper for authenticated fetch
     */
    async safeFetch(url, options = {}) {
        const token = localStorage.getItem('auth_token');
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
        if (options.body && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }
        
        const response = await fetch(url, { ...options, headers });
        if (response.status === 401) {
            console.warn("[Auth] Token expired or invalid. Redirecting to login.");
            window.location.href = '/login.html';
            return null;
        }
        return response;
    },

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
     * Opens WhatsApp with a pre-filled message
     * @param {string} phone - Target phone number
     * @param {string} message - Message text
     */
    openWhatsApp(phone, message = "Hola, te contacto desde Carbones y Pollos.") {
        if (!phone) {
            this.notify("Número de teléfono no disponible", "error");
            return;
        }
        const cleanPhone = phone.replace(/\D/g, '');
        const url = `https://wa.me/${cleanPhone.startsWith('34') ? cleanPhone : '34' + cleanPhone}?text=${encodeURIComponent(message)}`;
        window.open(url, '_blank');
    },

    /**
     * Panel de Tareas Operativas Premium (Centro de Mando)
     */
    renderQuickTaskPanel(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="glass-premium p-10 hover-premium animate-premium-entry border-l-4 border-l-indigo-600">
                <div class="flex items-center justify-between mb-8">
                    <div>
                        <h3 class="text-xl font-black text-slate-900 uppercase tracking-tighter">Centro de Mando</h3>
                        <p class="text-[10px] text-slate-400 font-bold uppercase mt-1">Gestión de Incidencias en Tiempo Real</p>
                    </div>
                    <div class="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center animate-float">
                        <span class="material-symbols-outlined text-indigo-600">bolt</span>
                    </div>
                </div>

                <div class="space-y-6">
                    <div class="relative">
                        <input type="text" id="task-title" class="input-premium w-full pr-12" placeholder="¿Qué ha pasado? Describir incidencia...">
                        <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-slate-300">edit_note</span>
                    </div>

                    <div class="grid grid-cols-3 gap-4">
                        <button onclick="document.getElementById('task-priority').value='ALTA'" class="p-4 rounded-2xl border border-slate-100 text-[10px] font-black uppercase transition-all hover:bg-rose-50 hover:text-rose-600 hover:border-rose-100">Alta</button>
                        <button onclick="document.getElementById('task-priority').value='MEDIA'" class="p-4 rounded-2xl border border-slate-100 text-[10px] font-black uppercase transition-all hover:bg-amber-50 hover:text-amber-600 hover:border-amber-100">Media</button>
                        <button onclick="document.getElementById('task-priority').value='BAJA'" class="p-4 rounded-2xl border border-slate-100 text-[10px] font-black uppercase transition-all hover:bg-emerald-50 hover:text-emerald-600 hover:border-emerald-100">Baja</button>
                    </div>
                    
                    <input type="hidden" id="task-priority" value="MEDIA">

                    <button id="btn-save-task" class="w-full py-5 bg-slate-900 hover:bg-black text-white rounded-2xl font-black text-[11px] uppercase tracking-widest transition-all shadow-2xl flex items-center justify-center gap-3 group">
                        <span>Lanzar Operativa</span>
                        <span class="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">send</span>
                    </button>
                </div>

                <div id="quick-tasks-list" class="mt-10 space-y-4 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
                    <!-- Tareas cargadas dinámicamente -->
                </div>
            </div>
        `;

        const btnSave = document.getElementById('btn-save-task');
        const inputTitle = document.getElementById('task-title');
        const selectPriority = document.getElementById('task-priority');

        const loadTasks = async () => {
            try {
                const response = await this.safeFetch('/api/admin/tasks');
                if (!response) return;
                const tasks = await response.json();
                const list = document.getElementById('quick-tasks-list');
                if (!tasks.length) {
                    list.innerHTML = '<p class="text-[9px] text-center text-slate-400 uppercase font-bold py-4">No hay tareas pendientes</p>';
                    return;
                }
                list.innerHTML = tasks.map(t => `
                    <div class="p-3 bg-white/80 border border-slate-100 rounded-2xl flex items-center justify-between group hover:border-amber-500/30 transition-all">
                        <div class="flex flex-col gap-1">
                            <span class="text-[11px] font-bold text-slate-800 line-clamp-1">${t.titulo}</span>
                            <div class="flex items-center gap-2">
                                ${this.createBadge(t.prioridad, t.prioridad === 'CRITICA' ? 'error' : (t.prioridad === 'ALTA' ? 'warning' : 'info'))}
                                <span class="text-[8px] text-slate-400 font-bold">${new Date(t.fecha).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                            </div>
                        </div>
                        <button onclick="updateTaskStatus('${t.id}')" class="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-emerald-500 hover:text-white transition-all">
                            <i class="fa-solid fa-check text-[10px]"></i>
                        </button>
                    </div>
                `).join('');
            } catch (err) {
                console.error("Error cargando tareas:", err);
            }
        };

        window.updateTaskStatus = async (id) => {
            try {
                await this.safeFetch(`/api/admin/tasks/${id}`, {
                    method: 'PATCH',
                    body: JSON.stringify({ estado: 'COMPLETADO' })
                });
                loadTasks();
            } catch (err) {
                this.notify("Error al actualizar tarea", "error");
            }
        };

        btnSave.onclick = async () => {
            const titulo = inputTitle.value.trim();
            if (!titulo) return;

            btnSave.disabled = true;
            try {
                const res = await this.safeFetch('/api/admin/tasks', {
                    method: 'POST',
                    body: JSON.stringify({ titulo, prioridad: selectPriority.value })
                });
                if (res.ok) {
                    inputTitle.value = '';
                    loadTasks();
                    this.notify("Tarea guardada correctamente", "success");
                }
            } catch (err) {
                this.notify("Fallo al guardar tarea", "error");
            } finally {
                btnSave.disabled = false;
            }
        };

        loadTasks();
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
    },

    /**
     * Renderizador de Estados Vacíos Contextuales
     * @param {string} containerId - ID del contenedor
     * @param {Object} options - Configuración (title, message, icon, ctaLabel, ctaAction)
     */
    renderEmptyState(containerId, options) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const html = `
            <div class="flex flex-col items-center justify-center py-20 px-6 text-center animate-premium-entry">
                <div class="w-24 h-24 rounded-[2.5rem] bg-slate-50 border border-slate-100 flex items-center justify-center mb-8 shadow-inner animate-float">
                    <span class="material-symbols-outlined text-5xl text-slate-300">${options.icon || 'inventory_2'}</span>
                </div>
                <h3 class="text-xl font-black text-slate-900 uppercase tracking-tight mb-2">${options.title || 'Sin Datos Disponibles'}</h3>
                <p class="text-xs text-slate-400 font-medium max-w-[280px] leading-relaxed mb-10">${options.message || 'No se han encontrado registros en este módulo. Inicia una nueva acción para comenzar.'}</p>
                ${options.ctaLabel ? `
                    <button onclick="${options.ctaAction}" class="px-10 py-5 bg-indigo-600 hover:bg-indigo-700 text-white font-black text-[11px] uppercase tracking-widest rounded-3xl transition-all shadow-2xl shadow-indigo-100 hover:scale-105 active:scale-95 flex items-center gap-3">
                        <span class="material-symbols-outlined text-[18px]">add_circle</span>
                        ${options.ctaLabel}
                    </button>
                ` : ''}
            </div>
        `;
        container.innerHTML = html;
    },

    /**
     * Motor de Autocompletado Transversal Premium
     */
    setupAutocomplete(inputId, type, onSelect) {
        const input = document.getElementById(inputId);
        if (!input) return;

        const container = document.createElement('div');
        container.className = 'absolute z-[1000] w-full bg-white/90 backdrop-blur-xl border border-slate-100 rounded-[2rem] shadow-2xl mt-4 hidden max-h-80 overflow-y-auto animate-premium-entry p-2';
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(container);

        let timeout;
        input.addEventListener('input', () => {
            clearTimeout(timeout);
            const q = input.value.trim();
            if (q.length < 2) {
                container.innerHTML = '';
                container.classList.add('hidden');
                return;
            }

            timeout = setTimeout(async () => {
                try {
                    const res = await this.safeFetch(`/api/autocomplete/${type}?q=${encodeURIComponent(q)}`);
                    if (!res) return;
                    const data = await res.json();
                    
                    if (data.length === 0) {
                        container.innerHTML = '<div class="p-8 text-[10px] font-black text-slate-300 uppercase text-center">Sin resultados operativos</div>';
                    } else {
                        container.innerHTML = data.map(item => `
                            <div class="p-5 hover:bg-indigo-50/50 rounded-2xl cursor-pointer transition-all flex justify-between items-center group mb-1" data-id="${item.id}">
                                <div>
                                    <p class="text-xs font-black text-slate-900 uppercase tracking-tight">${item.text}</p>
                                    ${item.rol ? `<p class="text-[8px] text-slate-400 font-bold uppercase mt-1 tracking-widest">${item.rol}</p>` : ''}
                                    ${item.direccion ? `<p class="text-[8px] text-slate-400 font-bold uppercase mt-1 tracking-widest">${item.direccion}</p>` : ''}
                                </div>
                                <span class="material-symbols-outlined text-slate-200 group-hover:text-indigo-600 transition-all group-hover:scale-110">add_circle</span>
                            </div>
                        `).join('');

                        container.querySelectorAll('[data-id]').forEach((el, index) => {
                            el.addEventListener('click', () => {
                                const selected = data[index];
                                input.value = selected.text;
                                container.classList.add('hidden');
                                if (onSelect) onSelect(selected);
                            });
                        });
                    }
                    container.classList.remove('hidden');
                } catch (e) { console.error("Autocomplete Error:", e); }
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !container.contains(e.target)) {
                container.classList.add('hidden');
            }
        });
    },

    /**
     * Renderizador de KPIs Premium con Animación y Glow
     */
    renderPremiumKPI(containerId, options) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const html = `
            <div class="glass-premium p-10 hover-premium animate-premium-entry relative overflow-hidden group">
                <div class="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                    <span class="material-symbols-outlined text-7xl">${options.icon || 'analytics'}</span>
                </div>
                <div class="relative z-10">
                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-6">${options.label}</p>
                    <div class="flex items-baseline gap-3">
                        <h2 class="text-5xl font-black text-slate-900 tracking-tighter data-glow">${options.value}</h2>
                        ${options.trend ? `
                            <span class="px-3 py-1 rounded-full bg-${options.trend > 0 ? 'emerald' : 'rose'}-50 text-[10px] font-black ${options.trend > 0 ? 'text-emerald-600' : 'text-rose-600'} flex items-center gap-1">
                                <span class="material-symbols-outlined text-[14px]">${options.trend > 0 ? 'trending_up' : 'trending_down'}</span>
                                ${Math.abs(options.trend)}%
                            </span>
                        ` : ''}
                    </div>
                    <div class="mt-8 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden shadow-inner">
                        <div class="h-full ${options.colorClass || 'bg-gradient-premium-indigo'} transition-all duration-1000 ease-out" style="width: ${options.progress || 0}%"></div>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML = html;
    }
};

// Auto-inicialización Premium
EnterpriseUI.injectStyles = function() {
    if (!document.querySelector('link[href*="premium_industrial.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/premium_industrial.css';
        document.head.appendChild(link);
    }
};
EnterpriseUI.injectStyles();

window.EnterpriseUI = EnterpriseUI;
