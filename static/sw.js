const CACHE_NAME = 'tpv-pollos-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/kiosko.html',
  '/static/setup.html',
  '/static/caja.html',
  '/static/cocina.html',
  '/static/admin/index.html',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap',
  'https://cdn-icons-png.flaticon.com/512/3075/3075977.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Usamos catch para que si falla una URL externa no falle todo el Service Worker
      return Promise.allSettled(ASSETS_TO_CACHE.map(url => cache.add(url)));
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[SW] Limpiando cache antigua:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Estrategia: Network First con Fallback a Cache (para datos frescos)
// O Cache First para estáticos (ya cacheado en ASSETS_TO_CACHE)
self.addEventListener('fetch', (event) => {
  // Solo cachear GETs
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) return cachedResponse;

      return fetch(event.request).then((networkResponse) => {
        // No cachear llamadas a la API (datos vivos)
        if (!event.request.url.includes('/api/')) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        // Fallback offline para imágenes si fallan
        if (event.request.destination === 'image') {
          return caches.match('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        }
      });
    })
  );
});
