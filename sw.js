// Service worker de CASANDRA: funciona sin conexión una vez cargada la app.
// Sube este archivo junto a index.html (misma carpeta). Si cambias la app, sube la versión de CACHE.
const CACHE = 'casandra-v2';
const SHELL = ['./', 'index.html', 'manifest.json'];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE)
            .then((c) => c.addAll(SHELL))
            .catch(() => {})
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const req = e.request;
    if (req.method !== 'GET' || !/^https?:/.test(req.url)) return;
    if (new URL(req.url).pathname.startsWith('/_vercel/')) return; // analíticas: nunca cachear

    // Páginas: red primero (siempre la última versión) y caché si no hay conexión
    if (req.mode === 'navigate') {
        e.respondWith(
            fetch(req)
                .then((res) => {
                    const copy = res.clone();
                    caches.open(CACHE).then((c) => c.put(req, copy));
                    return res;
                })
                .catch(() => caches.match(req).then((r) => r || caches.match('index.html')))
        );
        return;
    }

    // Resto (Tailwind, fuentes, html2canvas…): caché al instante y se refresca en segundo plano
    e.respondWith(
        caches.open(CACHE).then(async (cache) => {
            const cached = await cache.match(req);
            const network = fetch(req)
                .then((res) => {
                    if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
                    return res;
                })
                .catch(() => cached);
            return cached || network;
        })
    );
});
