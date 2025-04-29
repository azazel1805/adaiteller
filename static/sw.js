const CACHE_NAME = 'story-generator-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
  // Add other essential assets if needed
];

// Install event: Cache essential assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting(); // Activate worker immediately
});

// Fetch event: Serve from cache if available, otherwise fetch from network
self.addEventListener('fetch', event => {
  // Skip caching for POST requests (form submissions)
  if (event.request.method === 'POST') {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        // Not in cache - fetch from network
        return fetch(event.request).then(
          networkResponse => {
            // Optional: Cache new requests dynamically (be careful with this)
            // if(!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
            //   return networkResponse;
            // }
            // const responseToCache = networkResponse.clone();
            // caches.open(CACHE_NAME)
            //   .then(cache => {
            //     cache.put(event.request, responseToCache);
            //   });
            return networkResponse;
          }
        );
      })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim(); // Take control of pages immediately
});
