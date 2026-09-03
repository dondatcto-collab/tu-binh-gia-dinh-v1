const CACHE = 'tubinh-ui-v3.2.1-trust-first';
const SHELL = [
  '/',
  '/static/app.css?v=0.5.0',
  '/static/app.js?v=0.5.0',
  '/static/ui-language-051.js?v=0.5.1',
  '/static/ui-bootstrap-v26.js?v=2.6',
  '/static/ui-bootstrap-v26.js?v=2.7',
  '/static/ui-event-search-v27.js?v=2.7',
  '/manifest.webmanifest',
  '/icon-192.png',
  '/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET') return;
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(req, {cache: 'no-store'}));
    return;
  }
  if (req.mode === 'navigate') {
    event.respondWith(fetch(req, {cache: 'no-store'}).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put('/', copy));
      return res;
    }).catch(() => caches.match('/')));
    return;
  }
  event.respondWith(fetch(req).then(res => {
    if (res.ok) {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(req, copy));
    }
    return res;
  }).catch(() => caches.match(req)));
});
