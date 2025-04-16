/**
 * Service Worker for Ukombozini Management System
 * Handles offline caching of assets and API responses
 */

const CACHE_NAME = 'ukombozini-cache-v1';
const urlsToCache = [
  '/',
  '/templates/offline.html',
  '/offline.html', // Add alternative path to improve resilience
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/img/logo.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Handle API requests differently than static assets
  const isApiRequest = event.request.url.includes('/api/');
  const isHTMLRequest = event.request.url.endsWith('.html') || 
                        event.request.url.endsWith('/') ||
                        !event.request.url.match(/\.[a-z]+$/i);

  if (isApiRequest) {
    // For API requests, try network first, then cache
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache a copy of the response
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          return response;
        })
        .catch(() => {
          // If network fails, try the cache
          return caches.match(event.request);
        })
    );
  } else if (isHTMLRequest) {
    // For HTML/route requests, try network first (for fresh content)
    // But fall back to cache or offline page
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache a copy of the response
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          return response;
        })
        .catch(() => {
          // If network fails, try the cache
          return caches.match(event.request)
            .then((response) => {
              if (response) {
                return response;
              }
              // If no match in cache, serve offline page
              return caches.match('/templates/offline.html')
                .then(response => {
                  if (response) return response;
                  // Try alternative path as fallback
                  return caches.match('/offline.html');
                });
            });
        })
    );
  } else {
    // For other static assets, use cache-first strategy
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Return from cache if found
          if (response) {
            return response;
          }
          
          // Otherwise fetch from network
          return fetch(event.request)
            .then((response) => {
              // Cache the new resource
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache);
                });
              return response;
            });
        })
    );
  }
});

// Handle sync events for background syncing
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pending-data') {
    event.waitUntil(syncPendingData());
  }
});

// Function to sync pending data
async function syncPendingData() {
  // This is handled by the main OfflineManager class
  // But we could implement additional sync logic here if needed
  console.log('Background sync triggered');
  
  // Notify all clients that a sync was triggered
  const clients = await self.clients.matchAll();
  for (const client of clients) {
    client.postMessage({
      type: 'sync-triggered',
      timestamp: new Date().toISOString()
    });
  }
}

// Handle push notifications
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.message || 'New notification',
    icon: '/static/images/logo.png',
    badge: '/static/images/notification-badge.png',
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification('Ukombozini Management System', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.matchAll({type: 'window'})
      .then((clientList) => {
        // If a window is already open, focus it
        for (const client of clientList) {
          if (client.url === event.notification.data.url && 'focus' in client) {
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow(event.notification.data.url);
        }
      })
  );
}); 