/**
 * Offline Manager for Ukombozini Management System
 * Handles offline storage, synchronization, and notifications
 */

class OfflineManager {
    constructor() {
        this.dbName = 'ukomboziniOfflineDB';
        this.dbVersion = 1;
        this.pendingSync = [];
        this.db = null;
        this.isOnline = navigator.onLine;
        this.notificationContainer = null;
        this.syncInterval = null;

        // Initialize database
        this.initDB();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Register service worker
        this.registerServiceWorker();
        
        // Create notification container
        this.createNotificationContainer();
        
        // Start sync process on a timer
        this.startSyncInterval();
    }

    /**
     * Initialize IndexedDB
     */
    initDB() {
        const request = indexedDB.open(this.dbName, this.dbVersion);
        
        request.onerror = (event) => {
            this.showNotification('Database Error', 'Could not open offline database.', 'error');
            console.error("IndexedDB error:", event.target.errorCode);
        };
        
        request.onsuccess = (event) => {
            this.db = event.target.result;
            console.log("Database initialized successfully");
            
            // Check for pending data to sync when we come online
            if (this.isOnline) {
                this.syncData();
            }
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create object stores for different data types
            if (!db.objectStoreNames.contains('pendingRequests')) {
                const pendingStore = db.createObjectStore('pendingRequests', { keyPath: 'id', autoIncrement: true });
                pendingStore.createIndex('url', 'url', { unique: false });
                pendingStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
            
            // Create stores for cached data
            const dataTypes = ['members', 'payments', 'visits', 'events', 'settings'];
            dataTypes.forEach(type => {
                if (!db.objectStoreNames.contains(type)) {
                    const store = db.createObjectStore(type, { keyPath: 'id' });
                    store.createIndex('lastModified', 'lastModified', { unique: false });
                }
            });
        };
    }

    /**
     * Setup event listeners for online/offline events
     */
    setupEventListeners() {
        // Network status events
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateConnectionUI();
            this.showNotification('Connection Restored', 'You are now online. Syncing data...', 'info');
            this.syncData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateConnectionUI();
            this.showNotification('Connection Lost', 'You are working offline. Changes will be saved and synced when connection is restored.', 'warning');
        });
        
        // Intercept form submissions when offline
        document.addEventListener('submit', (event) => {
            if (!this.isOnline && !event.target.hasAttribute('data-allow-offline')) {
                event.preventDefault();
                this.handleOfflineFormSubmission(event.target);
            }
        });
        
        // Intercept AJAX requests
        this.setupFetchInterceptor();
    }

    /**
     * Update UI elements that show connection status
     */
    updateConnectionUI() {
        // Update status indicator in navigation
        const statusEl = document.querySelector('.connection-status');
        const statusTextEl = document.querySelector('.connection-status-text');
        
        if (statusEl) {
            if (this.isOnline) {
                statusEl.classList.remove('status-offline');
                statusEl.classList.add('status-online');
                statusTextEl.textContent = 'Online';
            } else {
                statusEl.classList.remove('status-online');
                statusEl.classList.add('status-offline');
                statusTextEl.textContent = 'Offline';
            }
        }
        
        // Update sync indicator if it exists
        const syncIndicator = document.querySelector('.sync-indicator');
        if (syncIndicator) {
            syncIndicator.classList.toggle('syncing', this.pendingSync.length > 0);
            
            // Show sync badge with count if we have pending items
            const syncBadge = syncIndicator.querySelector('.sync-badge');
            if (this.pendingSync.length > 0) {
                if (syncBadge) {
                    syncBadge.textContent = this.pendingSync.length > 99 ? '99+' : this.pendingSync.length;
                } else {
                    const badge = document.createElement('span');
                    badge.className = 'sync-badge';
                    badge.textContent = this.pendingSync.length > 99 ? '99+' : this.pendingSync.length;
                    syncIndicator.appendChild(badge);
                }
            } else if (syncBadge) {
                syncBadge.remove();
            }
        }
    }

    /**
     * Register service worker for offline caching
     */
    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered with scope:', registration.scope);
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        }
    }

    /**
     * Create notification container for displaying messages
     */
    createNotificationContainer() {
        if (!document.querySelector('.offline-notification-container')) {
            this.notificationContainer = document.createElement('div');
            this.notificationContainer.className = 'offline-notification-container';
            document.body.appendChild(this.notificationContainer);
        } else {
            this.notificationContainer = document.querySelector('.offline-notification-container');
        }
    }

    /**
     * Show a notification message
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {string} type - Type of notification (info, success, warning, error)
     * @param {number} duration - Duration in ms before auto-closing (0 = no auto-close)
     */
    showNotification(title, message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `offline-notification ${type}`;
        
        notification.innerHTML = `
            <h5 class="title">${title}</h5>
            <p class="message">${message}</p>
            <span class="close-btn">&times;</span>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Add close button handler
        const closeBtn = notification.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOut 0.3s forwards';
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Auto-close after duration (if specified)
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOut 0.3s forwards';
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 300);
                }
            }, duration);
        }
        
        return notification;
    }

    /**
     * Start interval to check and sync data periodically
     */
    startSyncInterval() {
        // Try to sync every 30 seconds when online
        this.syncInterval = setInterval(() => {
            if (this.isOnline && this.pendingSync.length > 0) {
                this.syncData();
            }
        }, 30000);
    }

    /**
     * Handle form submissions when offline
     * @param {HTMLFormElement} form - The form being submitted
     */
    handleOfflineFormSubmission(form) {
        // Get form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        // Get form action and method
        const url = form.action || window.location.href;
        const method = form.method.toUpperCase() || 'GET';
        
        // Add to pending requests
        this.addPendingRequest(url, method, data);
        
        // Show notification
        this.showNotification('Saved Offline', 'Your changes will be submitted when your connection is restored.', 'info');
        
        // Highlight form as being saved offline
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.classList.add('offline-form-control');
        });
        
        // Reset form if needed
        if (form.hasAttribute('data-reset-after-offline-save')) {
            form.reset();
        }
    }

    /**
     * Setup fetch interceptor to handle offline requests
     */
    setupFetchInterceptor() {
        const originalFetch = window.fetch;
        
        window.fetch = async (url, options = {}) => {
            // If online, proceed with normal fetch
            if (this.isOnline) {
                return originalFetch(url, options);
            }
            
            // If offline, store the request for later and return a mock response
            const method = options.method || 'GET';
            const body = options.body || null;
            
            // Allow GET requests to try to fetch from cache via service worker
            if (method === 'GET') {
                try {
                    const response = await originalFetch(url, options);
                    return response;
                } catch (error) {
                    // If fetch fails (no cache/network), check our IndexedDB cache
                    return this.getFromOfflineCache(url);
                }
            }
            
            // For non-GET requests, store them for later
            let data = null;
            if (body) {
                if (typeof body === 'string') {
                    try {
                        data = JSON.parse(body);
                    } catch (e) {
                        data = body;
                    }
                } else if (body instanceof FormData) {
                    data = {};
                    for (const [key, value] of body.entries()) {
                        data[key] = value;
                    }
                }
            }
            
            this.addPendingRequest(url, method, data);
            
            // Return a mock successful response
            return new Response(JSON.stringify({ 
                success: true, 
                message: 'Request saved for offline sync', 
                offline: true 
            }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        };
    }

    /**
     * Get data from offline cache
     * @param {string} url - URL being requested
     * @returns {Promise<Response>} - Mocked response with cached data or 404
     */
    async getFromOfflineCache(url) {
        // Extract the data type from the URL
        const urlPath = new URL(url, window.location.origin).pathname;
        const match = urlPath.match(/\/api\/([a-z]+)(?:\/(\d+))?/);
        
        if (!match) {
            return new Response(JSON.stringify({ error: 'Not found in offline cache' }), {
                status: 404,
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        const dataType = match[1];
        const id = match[2];
        
        if (!this.db) {
            return new Response(JSON.stringify({ error: 'Offline database not available' }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        return new Promise((resolve) => {
            // If we have an ID, get the specific item
            if (id) {
                const transaction = this.db.transaction([dataType], 'readonly');
                const store = transaction.objectStore(dataType);
                const request = store.get(parseInt(id, 10));
                
                request.onsuccess = () => {
                    if (request.result) {
                        resolve(new Response(JSON.stringify(request.result), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        }));
                    } else {
                        resolve(new Response(JSON.stringify({ error: 'Not found in offline cache' }), {
                            status: 404,
                            headers: { 'Content-Type': 'application/json' }
                        }));
                    }
                };
                
                request.onerror = () => {
                    resolve(new Response(JSON.stringify({ error: 'Error accessing offline cache' }), {
                        status: 500,
                        headers: { 'Content-Type': 'application/json' }
                    }));
                };
            } else {
                // Get all items of this type
                const transaction = this.db.transaction([dataType], 'readonly');
                const store = transaction.objectStore(dataType);
                const request = store.getAll();
                
                request.onsuccess = () => {
                    resolve(new Response(JSON.stringify(request.result || []), {
                        status: 200,
                        headers: { 'Content-Type': 'application/json' }
                    }));
                };
                
                request.onerror = () => {
                    resolve(new Response(JSON.stringify({ error: 'Error accessing offline cache' }), {
                        status: 500,
                        headers: { 'Content-Type': 'application/json' }
                    }));
                };
            }
        });
    }

    /**
     * Add a pending request to be synced later
     * @param {string} url - Request URL
     * @param {string} method - HTTP method
     * @param {object} data - Request payload
     */
    addPendingRequest(url, method, data) {
        if (!this.db) {
            console.error('Cannot save offline request: database not initialized');
            return;
        }
        
        const transaction = this.db.transaction(['pendingRequests'], 'readwrite');
        const store = transaction.objectStore('pendingRequests');
        
        const request = {
            url: url,
            method: method,
            data: data,
            timestamp: new Date().toISOString()
        };
        
        store.add(request);
        
        // Add to pending sync array for UI updates
        this.pendingSync.push(request);
        this.updateConnectionUI();
    }

    /**
     * Sync pending data with the server
     */
    syncData() {
        if (!this.isOnline || !this.db) {
            return;
        }
        
        const transaction = this.db.transaction(['pendingRequests'], 'readwrite');
        const store = transaction.objectStore('pendingRequests');
        const request = store.getAll();
        
        request.onsuccess = async () => {
            const requests = request.result;
            
            if (requests.length === 0) {
                return;
            }
            
            this.showNotification('Syncing', `Syncing ${requests.length} pending ${requests.length === 1 ? 'change' : 'changes'}...`, 'info');
            
            let successCount = 0;
            let failCount = 0;
            
            // Process each pending request
            for (const pendingRequest of requests) {
                try {
                    const response = await fetch(pendingRequest.url, {
                        method: pendingRequest.method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Offline-Sync': 'true'
                        },
                        body: JSON.stringify(pendingRequest.data)
                    });
                    
                    if (response.ok) {
                        // Delete from pending store on success
                        const deleteTransaction = this.db.transaction(['pendingRequests'], 'readwrite');
                        const deleteStore = deleteTransaction.objectStore('pendingRequests');
                        deleteStore.delete(pendingRequest.id);
                        successCount++;
                    } else {
                        failCount++;
                    }
                } catch (error) {
                    console.error('Sync error:', error);
                    failCount++;
                }
            }
            
            // Update the UI
            this.pendingSync = this.pendingSync.slice(successCount);
            this.updateConnectionUI();
            
            // Show completion notification
            if (successCount > 0) {
                this.showNotification('Sync Complete', `Successfully synced ${successCount} ${successCount === 1 ? 'change' : 'changes'}.`, 'success');
            }
            
            if (failCount > 0) {
                this.showNotification('Sync Issues', `Failed to sync ${failCount} ${failCount === 1 ? 'change' : 'changes'}. Will retry later.`, 'warning', 10000);
            }
        };
        
        request.onerror = () => {
            console.error('Error accessing pending requests:', request.error);
        };
    }

    /**
     * Store data in the offline cache
     * @param {string} type - Data type/store name
     * @param {object} data - Data to store
     */
    storeOfflineData(type, data) {
        if (!this.db) {
            console.error('Cannot store offline data: database not initialized');
            return;
        }
        
        // Ensure type is valid
        if (!this.db.objectStoreNames.contains(type)) {
            console.error(`Invalid store type: ${type}`);
            return;
        }
        
        const transaction = this.db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        
        if (Array.isArray(data)) {
            // For arrays, add each item individually
            data.forEach(item => {
                // Ensure the item has a lastModified timestamp
                if (!item.lastModified) {
                    item.lastModified = new Date().toISOString();
                }
                store.put(item);
            });
        } else {
            // For single items
            if (!data.lastModified) {
                data.lastModified = new Date().toISOString();
            }
            store.put(data);
        }
    }

    /**
     * Clear the offline cache for a specific type
     * @param {string} type - Data type/store name
     */
    clearOfflineCache(type) {
        if (!this.db) {
            return;
        }
        
        if (!type || !this.db.objectStoreNames.contains(type)) {
            return;
        }
        
        const transaction = this.db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        store.clear();
    }
}

// Initialize the offline manager
const offlineManager = new OfflineManager();

// Make it globally accessible
window.offlineManager = offlineManager; 