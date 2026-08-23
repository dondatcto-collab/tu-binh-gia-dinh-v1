const CACHE='tubinh-v1-shell-7';
const SHELL=['/','/static/app.css','/static/app.js','/manifest.webmanifest','/icon-192.png','/icon-512.png','/avatars/old-male.png','/avatars/old-female.png','/avatars/adult-male.png','/avatars/adult-female.png','/avatars/youth-male.png','/avatars/youth-female.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.pathname.startsWith('/api/'))return;e.respondWith(fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r;}).catch(()=>caches.match(e.request).then(r=>r||caches.match('/'))));});
