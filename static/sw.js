const CACHE_NAME = 'adai-teller-cache-v2'; // Increment version if you change cached files
const urlsToCache = [
  '/', // The root page (index.html served by Flask)
  '/static/css/style.css',        // Your specific CSS file
  '/static/js/script.js',         // Your specific JS logic file
  '/static/js/main.js',           // The SW registration script
  '/static/manifest.json',        // The PWA manifest
  '/static/images/icons/icon-192x192.png', // PWA icon
  '/static/images/icons/icon-512x512.png',  // PWA icon
  // Add other essential static assets if any (e.g., fonts loaded directly, logo image)
  // Be careful NOT to cache '/generate' API endpoint or dynamic content.
];

// Install event: Cache core assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell:', urlsToCache);
        return cache.addAll(urlsToCache);
      })
      .then(() => {
         console.log('[Service Worker] Skip waiting on install');
         return self.skipWaiting(); // Activate worker immediately
      })
      .catch(error => {
        console.error('[Service Worker] Cache addAll failed:', error);
      })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  const cacheWhitelist = [CACHE_NAME]; // Only keep the current cache version
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
         console.log('[Service Worker] Claiming clients');
         return self.clients.claim(); // Take control of open pages immediately
    })
  );
});

// Fetch event: Serve cached assets first, network fallback
self.addEventListener('fetch', event => {
  // We only want to cache GET requests for our static assets
  // We explicitly ignore the API endpoint '/generate' and non-GET requests
  if (event.request.method !== 'GET' || event.request.url.includes('/generate')) {
      // console.log('[Service Worker] Fetch event ignored for non-GET or API request:', event.request.url);
      // Let the browser handle it normally
      event.respondWith(fetch(event.request));
      return;
  }

  // Strategy: Cache-first, then network
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // console.log('[Service Worker] Serving from cache:', event.request.url);
          return cachedResponse;
        }

        // console.log('[Service Worker] Fetching from network:', event.request.url);
        return fetch(event.request).then(
          networkResponse => {
            // Optional: Cache dynamically fetched static assets if needed
            // Be careful here - only cache expected static assets if they weren't in the initial list
            // For this app, most static assets should be in urlsToCache.
            // if (networkResponse.ok && urlsToCache.includes(new URL(event.request.url).pathname)) {
            //   const responseToCache = networkResponse.clone();
            //   caches.open(CACHE_NAME).then(cache => {
            //     cache.put(event.request, responseToCache);
            //   });
            // }
            return networkResponse;
          }
        ).catch(error => {
            console.error('[Service Worker] Fetch failed:', error);
            // Optional: Return a fallback offline page if fetch fails
            // return caches.match('/offline.html'); // You would need to create and cache offline.html
            // For this app, we'll just let the browser show its default offline error for failed network requests
        });
      })
  );
});
