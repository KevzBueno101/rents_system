/**
 * WebSocket Client for Real-time Notifications
 * 
 * Provides real-time notification delivery via WebSocket.
 * Only runs if ENABLE_WEBSOCKET_NOTIFICATIONS is True.
 */

class NotificationSocket {
    constructor(options = {}) {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.isConnecting = false;
        this.isConnected = false;
        
        // Event callbacks
        this.onNotification = options.onNotification || (() => {});
        this.onReadUpdate = options.onReadUpdate || (() => {});
        this.onUnreadCount = options.onUnreadCount || (() => {});
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onError = options.onError || (() => {});
        
        // Feature flag check
        this.enabled = options.enabled || false;
        
        if (this.enabled) {
            this.connect();
        }
    }
    
    connect() {
        if (this.isConnecting || this.isConnected) {
            return;
        }
        
        this.isConnecting = true;
        
        try {
            // Determine WebSocket URL
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsHost = window.location.host;
            const wsUrl = `${wsProtocol}//${wsHost}/ws/notifications/`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Notification WebSocket connected');
                this.isConnecting = false;
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                this.onConnect();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('Notification WebSocket disconnected', event);
                this.isConnecting = false;
                this.isConnected = false;
                this.onDisconnect();
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('Notification WebSocket error:', error);
                this.isConnecting = false;
                this.onError(error);
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.isConnecting = false;
            this.onError(error);
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.isConnecting = false;
    }
    
    send(action, payload = {}) {
        if (!this.isConnected || !this.ws) {
            console.warn('WebSocket not connected, cannot send message');
            return;
        }
        
        try {
            const message = JSON.stringify({
                action: action,
                ...payload
            });
            this.ws.send(message);
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
        }
    }
    
    markRead(notificationId) {
        this.send('mark_read', { id: notificationId });
    }
    
    markAllRead() {
        this.send('mark_all_read');
    }
    
    deleteNotification(notificationId) {
        this.send('delete', { id: notificationId });
    }
    
    bulkMarkRead(notificationIds) {
        this.send('bulk_action', {
            bulk_action: 'mark_read',
            notification_ids: notificationIds
        });
    }
    
    bulkDelete(notificationIds) {
        this.send('bulk_action', {
            bulk_action: 'delete',
            notification_ids: notificationIds
        });
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'initial_payload':
                this.handleInitialPayload(data);
                break;
            case 'new_notification':
                this.onNotification(data.notification);
                break;
            case 'read_update':
                this.onReadUpdate(data.id);
                break;
            case 'all_read_update':
                this.onReadUpdate('all');
                break;
            case 'unread_count':
                this.onUnreadCount(data.count);
                break;
            case 'notification_deleted':
                this.onNotificationDeleted(data.id);
                break;
            case 'bulk_read_update':
                this.onBulkReadUpdate(data.count);
                break;
            case 'bulk_delete_update':
                this.onBulkDeleteUpdate(data.count);
                break;
            case 'error':
                console.error('WebSocket error:', data.message);
                this.onError(new Error(data.message));
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    handleInitialPayload(data) {
        // Set initial unread count
        this.onUnreadCount(data.unread_count);
        
        // Add initial notifications
        if (data.notifications && data.notifications.length > 0) {
            data.notifications.forEach(notification => {
                this.onNotification(notification);
            });
        }
    }
    
    onNotificationDeleted(notificationId) {
        // Remove notification from DOM
        const element = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (element) {
            element.remove();
        }
    }
    
    onBulkReadUpdate(count) {
        console.log(`Bulk marked ${count} notifications as read`);
        // Update UI for bulk read operation
        document.querySelectorAll('.notification-item.unread-notification').forEach(element => {
            element.classList.remove('unread-notification');
            const badge = element.querySelector('.badge.bg-primary');
            if (badge) {
                badge.remove();
            }
        });
    }
    
    onBulkDeleteUpdate(count) {
        console.log(`Bulk deleted ${count} notifications`);
        // Remove notifications from DOM
        document.querySelectorAll('.notification-item').forEach(element => {
            element.remove();
        });
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        
        // Exponential backoff
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
            this.maxReconnectDelay
        );
        
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
}

// Initialize notification socket if feature flag is enabled
document.addEventListener('DOMContentLoaded', function() {
    // Check if feature flag is enabled (injected via template context)
    const enableWebSocketNotifications = window.ENABLE_WEBSOCKET_NOTIFICATIONS || false;
    
    if (enableWebSocketNotifications) {
        window.notificationSocket = new NotificationSocket({
            enabled: true,
            onNotification: function(notification) {
                // Add notification to DOM
                addNotificationToDOM(notification);
                
                // Update badge
                updateNotificationBadge();
                
                // Show browser notification if permission granted
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification(notification.title, {
                        body: notification.message,
                        icon: '/static/favicon.ico',
                        tag: `notification-${notification.id}`
                    });
                }
            },
            onReadUpdate: function(notificationId) {
                if (notificationId === 'all') {
                    // Mark all as read
                    document.querySelectorAll('.notification-item.unread-notification').forEach(element => {
                        element.classList.remove('unread-notification');
                        const badge = element.querySelector('.badge.bg-primary');
                        if (badge) {
                            badge.remove();
                        }
                    });
                } else {
                    // Mark single as read
                    const element = document.querySelector(`[data-notification-id="${notificationId}"]`);
                    if (element) {
                        element.classList.remove('unread-notification');
                        const badge = element.querySelector('.badge.bg-primary');
                        if (badge) {
                            badge.remove();
                        }
                    }
                }
                updateNotificationBadge();
            },
            onUnreadCount: function(count) {
                updateNotificationBadge(count);
            },
            onError: function(error) {
                console.error('Notification socket error:', error);
            }
        });
        
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
});

// Helper functions
function addNotificationToDOM(notification) {
    const container = document.querySelector('.notification-list');
    if (!container) return;
    
    const notificationElement = document.createElement('div');
    notificationElement.className = `alert alert-${notification.color} mb-0 py-2 px-3 notification-item ${!notification.is_read ? 'unread-notification' : ''}`;
    notificationElement.setAttribute('data-notification-id', notification.id);
    notificationElement.setAttribute('data-link', notification.link);
    notificationElement.style.cursor = 'pointer';
    
    notificationElement.innerHTML = `
        <div class="d-flex gap-2">
            <i class="bi ${notification.icon}"></i>
            <div class="flex-grow-1">
                <strong>${notification.title}</strong>
                <div class="small">${notification.message}</div>
            </div>
            ${!notification.is_read ? '<span class="badge bg-primary rounded-pill" style="font-size: 0.7rem;">New</span>' : ''}
        </div>
    `;
    
    // Add click handler
    notificationElement.addEventListener('click', function() {
        if (window.notificationSocket) {
            window.notificationSocket.markRead(notification.id);
        }
        
        // Navigate to link if provided
        if (notification.link && notification.link !== 'None') {
            window.location.href = notification.link;
        }
    });
    
    // Insert at the beginning of the list
    container.insertBefore(notificationElement, container.firstChild);
    
    // Limit to 10 notifications in the dropdown
    const notifications = container.querySelectorAll('.notification-item');
    if (notifications.length > 10) {
        notifications[notifications.length - 1].remove();
    }
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (!badge) return;
    
    if (count !== undefined) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    } else {
        // Count current unread notifications
        const unreadCount = document.querySelectorAll('.notification-item.unread-notification').length;
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Export for global access
window.NotificationSocket = NotificationSocket;
