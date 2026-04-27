const CACHE_NAME = 'carbones-tpv-v2';
const urlsToCache = [
  './',
  './index.html',
  './cocina.html',
  './caja.html',
  './dashboard.html',
  './login.html',
  './manifest.json',
  'https://cdn.jsdelivr.net/npm/sweetalert2@11'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => cacheName !== CACHE_NAME).map(cacheName => {
          return caches.delete(cacheName);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Ignorar peticiones API para no cachear datos mutables dinámicos
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Network First, fallback to cache
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clonar y guardar en caché la última versión
        const responseToCache = response.clone();
        caches.open(CACHE_NAME)
          .then(cache => {
            cache.put(event.request, responseToCache);
          });
        return response;
      })
      .catch(() => {
        // Si la red falla, usar el caché
        return caches.match(event.request);
      })
  );
});
