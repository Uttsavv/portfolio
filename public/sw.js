// Cache the parts of the site that never change at a given URL: the versioned 3D models (?v=hash)
// and Astro's hashed scripts and styles. Pages themselves always come from the network.
const CACHE = 'assets-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  const immutable = (/\/models\/[^/]+\.glb$/.test(url.pathname) && url.searchParams.has('v')) || url.pathname.includes('/_astro/');
  if (!immutable) return;
  e.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const hit = await cache.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) {
        cache.put(req, res.clone());
        // drop older versions of the same model
        if (url.pathname.endsWith('.glb')) for (const k of await cache.keys()) { const u = new URL(k.url); if (u.pathname === url.pathname && u.search !== url.search) cache.delete(k); }
      }
      return res;
    }),
  );
});
