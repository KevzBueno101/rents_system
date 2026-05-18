/**
 * Real-time Dashboard Synchronization
 * Ensures stats cards and bills details update immediately
 * without requiring manual page refresh
 */

class DashboardSync {
    constructor() {
        this.cacheKey = 'dashboard_data_timestamp';
        this.syncInterval = 10000; // 10 seconds
        this.maxRetries = 3;
        this.currentRetry = 0;
        this.isPolling = false;
        this.lastDataHash = null;
        
        this.init();
    }

    init() {
        console.log('🔄 Initializing real-time dashboard sync...');
        
        // Start polling for dashboard updates
        this.startPolling();
        
        // Listen for visibility changes to optimize polling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopPolling();
            } else {
                this.startPolling();
            }
        });
        
        // Listen for custom events from other tabs/windows
        window.addEventListener('dashboard-update', (event) => {
            console.log('📡 Received dashboard update event:', event.detail);
            this.handleDashboardUpdate(event.detail);
        });
    }

    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        console.log('📡 Starting dashboard polling...');
        
        this.pollDashboard();
        this.pollInterval = setInterval(() => {
            this.pollDashboard();
        }, this.syncInterval);
    }

    stopPolling() {
        if (!this.isPolling) return;
        
        this.isPolling = false;
        console.log('⏸️ Stopping dashboard polling...');
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async pollDashboard() {
        try {
            const response = await fetch('/api/tenant/dashboard-data/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Check if data has actually changed
            const currentHash = this.hashData(data);
            if (currentHash === this.lastDataHash) {
                console.log('📊 Dashboard data unchanged, skipping update');
                return;
            }

            console.log('📊 Dashboard data updated, refreshing components...');
            this.lastDataHash = currentHash;
            this.handleDashboardUpdate(data);
            this.currentRetry = 0; // Reset retry counter on success

        } catch (error) {
            console.error('❌ Error polling dashboard:', error);
            this.currentRetry++;
            
            if (this.currentRetry <= this.maxRetries) {
                console.log(`🔄 Retrying dashboard poll (${this.currentRetry}/${this.maxRetries})...`);
                setTimeout(() => this.pollDashboard(), 2000 * this.currentRetry);
            } else {
                console.error('❌ Max retries reached, stopping polling');
                this.stopPolling();
                this.showErrorNotification();
            }
        }
    }

    handleDashboardUpdate(data) {
        // Update stats cards
        this.updateStatsCards(data);
        
        // Update bills details
        this.updateBillsDetails(data);
        
        // Update last update timestamp
        this.updateLastSyncTime();
        
        // Update any other dashboard components
        this.updateOtherComponents(data);
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('dashboard-data-updated', {
            detail: data
        }));
    }

    updateStatsCards(data) {
        // Update Current Balance
        const balanceElement = document.querySelector('[data-balance="current"]');
        if (balanceElement && data.balance !== undefined) {
            const balanceValue = `PHP ${parseFloat(data.balance).toFixed(2)}`;
            const balanceDisplay = balanceElement.querySelector('.metric-value');
            if (balanceDisplay) {
                balanceDisplay.textContent = balanceValue;
            }
            
            // Update balance status indicator
            this.updateBalanceStatus(balanceElement, data);
        }

        // Update Next Due Date
        const dueDateElement = document.querySelector('[data-balance="due-date"]');
        if (dueDateElement && data.summary) {
            const dueDateDisplay = dueDateElement.querySelector('.metric-value');
            if (dueDateDisplay) {
                if (data.summary.is_overdue) {
                    dueDateDisplay.innerHTML = '<span class="text-danger">OVERDUE</span>';
                } else if (data.summary.next_bill) {
                    const dueDate = new Date(data.summary.next_bill.due_date);
                    const formattedDate = dueDate.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    });
                    
                    dueDateDisplay.innerHTML = formattedDate;
                    
                    // Add urgency badge
                    const existingBadge = dueDateDisplay.querySelector('.badge');
                    if (existingBadge) existingBadge.remove();
                    
                    if (data.summary.days_until_due <= 7) {
                        const badge = document.createElement('small');
                        badge.className = 'badge bg-warning ms-1';
                        badge.textContent = `${data.summary.days_until_due} days`;
                        dueDateDisplay.appendChild(badge);
                    }
                } else {
                    dueDateDisplay.textContent = 'No bill';
                }
            }
        }

        // Update Payment Status
        const paymentStatusElement = document.querySelector('[data-balance="payment-status"]');
        if (paymentStatusElement && data.enhanced_status) {
            const statusDisplay = paymentStatusElement.querySelector('.metric-value');
            if (statusDisplay) {
                statusDisplay.textContent = data.payment_status_label || 'No bill';
            }
            
            // Update progress bar
            this.updatePaymentProgress(paymentStatusElement, data.enhanced_status);
            
            // Update status indicator
            this.updatePaymentStatusIndicator(paymentStatusElement, data);
        }
    }

    updateBillsDetails(data) {
        // Update payment overview section
        const paymentOverview = document.querySelector('#payment-overview');
        if (paymentOverview) {
            // Update latest payment
            const latestPaymentElement = paymentOverview.querySelector('[data-latest-payment]');
            if (latestPaymentElement && data.latest_payment) {
                const latestPaymentDisplay = latestPaymentElement.querySelector('strong');
                if (latestPaymentDisplay) {
                    const paymentDate = new Date(data.latest_payment.payment_date);
                    latestPaymentDisplay.textContent = paymentDate.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    });
                }
            }
            
            // Update total paid
            const totalPaidElement = paymentOverview.querySelector('[data-total-paid]');
            if (totalPaidElement && data.summary) {
                const totalPaidDisplay = totalPaidElement.querySelector('strong');
                if (totalPaidDisplay) {
                    totalPaidDisplay.textContent = `PHP ${parseFloat(data.summary.total_paid).toFixed(2)}`;
                }
            }
            
            // Update remaining balance
            const remainingBalanceElement = paymentOverview.querySelector('[data-remaining-balance]');
            if (remainingBalanceElement && data.balance !== undefined) {
                const remainingBalanceDisplay = remainingBalanceElement.querySelector('strong');
                if (remainingBalanceDisplay) {
                    remainingBalanceDisplay.textContent = `PHP ${parseFloat(data.balance).toFixed(2)}`;
                }
                
                // Update balance color
                remainingBalanceElement.className = remainingBalanceElement.className.replace(
                    /text-(danger|success|warning)/g, 
                    data.balance > 0 ? 'text-danger' : 'text-success'
                );
            }
        }
    }

    updateBalanceStatus(element, data) {
        const statusElement = element.querySelector('.metric-sub');
        if (statusElement) {
            let statusHtml = '';
            
            if (data.enhanced_status?.has_overdue) {
                statusHtml = '<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Overdue payment</span>';
            } else if (data.balance > 0) {
                statusHtml = '<span class="text-warning"><i class="bi bi-clock"></i> Payment needed</span>';
            } else {
                statusHtml = '<span class="text-success"><i class="bi bi-check-circle"></i> No outstanding balance</span>';
            }
            
            statusElement.innerHTML = statusHtml;
        }
        
        // Update pending bills count
        const extraElement = element.querySelector('.metric-extra');
        if (extraElement && data.enhanced_status) {
            if (data.enhanced_status.total_bills > 1) {
                extraElement.innerHTML = `<small class="text-muted">${data.enhanced_status.pending_bills} pending bill(s)</small>`;
            } else {
                extraElement.innerHTML = '';
            }
        }
    }

    updatePaymentProgress(element, enhancedStatus) {
        const progressContainer = element.querySelector('.progress');
        const progressText = element.querySelector('small.text-muted');
        
        if (progressContainer && enhancedStatus) {
            const percentage = enhancedStatus.total_bills > 0 
                ? Math.round((enhancedStatus.paid_bills / enhancedStatus.total_bills) * 100)
                : 0;
            
            progressContainer.style.width = `${percentage}%`;
            
            if (progressText) {
                progressText.textContent = `${enhancedStatus.paid_bills}/${enhancedStatus.total_bills} bills paid`;
            }
        }
    }

    updatePaymentStatusIndicator(element, data) {
        const statusElement = element.querySelector('.metric-sub');
        if (statusElement) {
            let statusHtml = '';
            
            if (data.enhanced_status?.has_urgent_payment) {
                statusHtml = '<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Action required</span>';
            } else if (data.balance > 0) {
                statusHtml = '<span class="text-warning"><i class="bi bi-clock"></i> Review billing details</span>';
            } else {
                statusHtml = '<span class="text-success"><i class="bi bi-check-circle"></i> Account is current</span>';
            }
            
            statusElement.innerHTML = statusHtml;
        }
    }

    updateOtherComponents(data) {
        // Update room info if it exists
        const roomElement = document.querySelector('[data-balance="room-info"]');
        if (roomElement && data.room) {
            const roomDisplay = roomElement.querySelector('.metric-value');
            if (roomDisplay) {
                roomDisplay.textContent = data.room.room_code;
            }
        }
        
        // Update notification count if it exists
        const notificationElement = document.querySelector('[data-notification-count]');
        if (notificationElement && data.unread_notifications !== undefined) {
            notificationElement.textContent = data.unread_notifications;
        }
    }

    updateLastSyncTime() {
        // Update last sync timestamp
        let syncIndicator = document.querySelector('[data-sync-indicator]');
        if (!syncIndicator) {
            syncIndicator = document.createElement('div');
            syncIndicator.setAttribute('data-sync-indicator', 'true');
            syncIndicator.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0, 123, 255, 0.9);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                transition: all 0.3s ease;
            `;
            document.body.appendChild(syncIndicator);
        }
        
        const now = new Date();
        syncIndicator.textContent = `🔄 ${now.toLocaleTimeString()}`;
        
        // Hide after 3 seconds
        setTimeout(() => {
            if (syncIndicator) {
                syncIndicator.style.opacity = '0';
                setTimeout(() => {
                    if (syncIndicator && syncIndicator.parentNode) {
                        syncIndicator.parentNode.removeChild(syncIndicator);
                    }
                }, 300);
            }
        }, 3000);
    }

    showErrorNotification() {
        // Show error notification to user
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        notification.innerHTML = `
            <button type="button" class="btn-close" data-bs-dismiss="alert">×</button>
            <strong>Sync Issue</strong><br>
            Unable to sync dashboard data. Please refresh the page.
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    hashData(data) {
        // Create simple hash of data to detect changes
        return JSON.stringify({
            balance: data.balance,
            payment_status: data.payment_status,
            total_bills: data.enhanced_status?.total_bills,
            paid_bills: data.enhanced_status?.paid_bills,
            next_bill_due: data.summary?.next_bill?.due_date,
            last_updated: data.last_updated
        });
    }

    // Public methods for manual triggering
    forceUpdate() {
        console.log('🔄 Forcing dashboard update...');
        this.pollDashboard();
    }

    destroy() {
        this.stopPolling();
        console.log('🛑 Dashboard sync destroyed');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.dashboardSync) {
        window.dashboardSync.destroy();
    }
    
    window.dashboardSync = new DashboardSync();
    
    // Make it globally available
    window.forceDashboardUpdate = () => window.dashboardSync.forceUpdate();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboardSync) {
        window.dashboardSync.destroy();
    }
});
