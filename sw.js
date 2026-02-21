// Minimal service worker for PWA installation
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

// No caching - just here to enable PWA
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});
