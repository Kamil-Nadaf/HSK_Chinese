/* HSK Sprint service worker: the page and dictionary come from the network when online (so updates arrive), audio is cached after first play. */
const V = 'hsk-sprint-v4';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;
  const audio = u.pathname.includes('/audio/');
  if (audio) {
    e.respondWith(caches.match(r).then(hit => hit || fetch(r).then(res => { const c = res.clone(); caches.open(V).then(ch => ch.put(r, c)); return res; })));
    return;
  }
  e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(V).then(ch => ch.put(r, c)); return res; }).catch(() => caches.match(r)));
});
