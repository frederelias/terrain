// LOTS — Terre de rang. Coquille hors ligne. Nettoie les caches des versions précédentes,
// sans toucher à celui de l'archive /ancien/.
const CACHE = 'lots-5.0';
const SHELL = ['./', './index.html', './manifest.webmanifest', './brand/enseigne-360.png', './brand/enseigne-800.png', './brand/paysage.jpg',
  './icon-192.png', './favicon-32.png', './confidentialite.html',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'];
const ABS = new Set(SHELL.map(u => new URL(u, self.registration.scope).href));
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && (k.startsWith('lots-rebrand-') || k.startsWith('terrain-') || (k.startsWith('lots-') && !k.startsWith('lots-ancien-')))).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  if (r.mode === 'navigate') { // page : réseau d'abord, pour recevoir les mises à jour ; cache si hors ligne
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', cp)); return res; }).catch(() => caches.match('./index.html')));
    return; }
  if (ABS.has(r.url)) e.respondWith(caches.match(r).then(x => x || fetch(r)));
});
