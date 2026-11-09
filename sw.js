const CACHE_NAME = 'casandra-pwa-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './css/main.css',
  './js/main.js',
  './manifest.json',
  'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
  'https://fonts.googleapis.com/css2?family=Special+Elite&family=VT323&display=swap'
];

// Instalación del SW y almacenamiento en caché de los recursos estáticos
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[CASANDRA SW] Cacheando archivos iniciales');
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Activación del SW y limpieza de cachés antiguas
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('[CASANDRA SW] Eliminando caché antigua:', key);
          return caches.delete(key);
        }
      }));
    }).then(() => self.clients.claim())
  );
});

// Estrategia: Cache First con fallback a Network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response; // Devuelve la versión en caché si existe
      }
      return fetch(event.request).then((networkResponse) => {
        // Opcional: Cachear dinámicamente peticiones nuevas exitosas
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      });
    }).catch(() => {
      // Fallback en caso de estar totalmente offline sin caché de una sub-página
      if (event.request.mode === 'navigate') {
        return caches.match('./index.html');
      }
    })
  );
});