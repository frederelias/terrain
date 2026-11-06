// Terrain — coquille hors ligne. Les tuiles de carte et les services
// gouvernementaux passent toujours par le réseau.
const CACHE = 'terrain-v4';
const SHELL = [
  './', './index.html', './manifest.webmanifest', './icon.svg',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = e.request.url;
  const shell = SHELL.some(s => u.endsWith(s.replace('./','')) ) || u.includes('cdnjs.cloudflare.com/ajax/libs/leaflet');
  if (shell) e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
