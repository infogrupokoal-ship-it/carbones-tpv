/**
 * 🛰️ SERVICE WORKER ENTERPRISE - CARBONES Y POLLOS TPV
 * Estrategia: Cache First with Network Fallback & Background Sync
 */

const CACHE_NAME = 'tpv-enterprise-v3.1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/index.html',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap',
    // Otros activos críticos se añaden dinámicamente
];

// Instalación y cacheo de activos críticos
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Limpieza de caches antiguos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.filter((name) => name !== CACHE_NAME)
                          .map((name) => caches.delete(name))
            );
        })
    );
    self.clients.claim();
});

// Estrategia de Fetch: Network First para API, Cache First para Estáticos
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // No cachear llamadas a la API (queremos datos reales siempre que haya red)
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                // Si la API falla, podrías retornar una respuesta offline guardada si fuera necesario
                return caches.match(event.request);
            })
        );
        return;
    }

    // Para activos estáticos (Imágenes, CSS, JS)
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request).then((fetchResponse) => {
                return caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, fetchResponse.clone());
                    return fetchResponse;
                });
            });
        })
    );
});

// Sincronización en segundo plano (Para pedidos offline)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-orders') {
        event.waitUntil(syncOrders());
    }
});

async function syncOrders() {
    console.log("🔄 Sincronizando pedidos pendientes...");
    // Lógica para enviar pedidos guardados en IndexedDB cuando vuelva la red
}
