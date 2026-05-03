const CACHE_NAME = 'tpv-enterprise-cache-v21.0';
const ASSETS_TO_CACHE = [
  '/',
  '/static/kiosko.html',
  '/static/nosotros.html',
  '/static/tracking.html',
  '/static/kds.html',
  '/static/portal.html',
  '/static/dashboard.html',
  '/static/dashboard_produccion.html',
  '/static/admin/system_logs.html',
  '/static/css/design_system.css',
  '/static/repartidores.html',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] 🚀 Instalando Ecosistema Enterprise v5.0');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(key => {
        if (key !== CACHE_NAME) {
          console.log('[SW] 🗑️ Purgando Caché Antigua:', key);
          return caches.delete(key);
        }
      })
    ))
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // API y Pagos: Network First (No cacheamos transacciones críticas)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  // Assets Estáticos: Cache First con Estrategia de Revalidación en Segundo Plano
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200) {
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, networkResponse.clone()));
        }
        return networkResponse;
      });
      return cachedResponse || fetchPromise;
    })
  );
});
