/**
 * 🛰️ SERVICE WORKER ENTERPRISE - CARBONES Y POLLOS TPV
 * Estrategia: Stale-While-Revalidate para estáticos & Network-First para API
 */

const CACHE_NAME = 'tpv-enterprise-v4.1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/index.html',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((name) => {
                    if (name !== CACHE_NAME) return caches.delete(name);
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Estrategia: Network-First con Fallback a Cache (Para API)
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Opcional: Cachear la última respuesta buena de la API
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request).then(response => {
                        if (response) return response;
                        return new Response(JSON.stringify({ error: "Offline Mode", offline: true }), {
                            headers: { 'Content-Type': 'application/json' }
                        });
                    });
                })
        );
        return;
    }

    // Estrategia: Stale-While-Revalidate (Para Estáticos)
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                    });
                }
                return networkResponse;
            }).catch(() => {
                // Manejo de errores de red en estáticos
                console.log("Network fallida para activo estático:", event.request.url);
            });

            // Retornar cache instantáneo si existe, de lo contrario esperar a la red
            return cachedResponse || fetchPromise;
        })
    );
});

// Sync en segundo plano
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-orders') {
        event.waitUntil(syncOrders());
    }
});

async function syncOrders() {
    console.log("🔄 Background Sync: Transmitiendo pedidos pendientes a la nube...");
    // Future: IndexedDB to Sync API
}
