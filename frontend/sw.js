const CACHE = 'estimate-v1';
const ASSETS = ['/', '/css/style.css', '/js/api.js', '/js/auth.js', '/js/components.js', '/js/estimates.js', '/js/calculator.js', '/js/app.js'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});

self.addEventListener('fetch', e => {
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
