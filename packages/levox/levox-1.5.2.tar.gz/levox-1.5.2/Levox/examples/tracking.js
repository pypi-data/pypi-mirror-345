/**
 * Example tracking module with GDPR compliance issues
 */

// Analytics service configuration
const analyticsConfig = {
    endpoint: 'https://analytics.example.com/track',
    batchSize: 10,
    flushInterval: 30000 // 30 seconds
};

// Queue for storing analytics events
let analyticsQueue = [];

/**
 * Track user behavior and send to analytics service
 * GDPR Issue: No consent check before tracking
 */
function logUserActivity(userIp, behavior) {
    const event = {
        timestamp: Date.now(),
        ip: userIp,
        action: behavior.action,
        page: behavior.page,
        duration: behavior.duration,
        sessionId: getCookie('session_id')
    };
    
    analyticsQueue.push(event);
    
    // If queue reaches batch size, send immediately
    if (analyticsQueue.length >= analyticsConfig.batchSize) {
        flushAnalyticsQueue();
    }
}

/**
 * Send analytics data to server
 */
function flushAnalyticsQueue() {
    if (analyticsQueue.length === 0) return;
    
    const data = JSON.stringify(analyticsQueue);
    
    // Create a new XMLHttpRequest
    const xhr = new XMLHttpRequest();
    xhr.open('POST', analyticsConfig.endpoint, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    // GDPR Issue: Sending tracking data without consent verification
    xhr.send(data);
    
    // Clear the queue after sending
    analyticsQueue = [];
}

/**
 * Get a cookie value by name
 */
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

/**
 * Set a tracking cookie
 * GDPR Issue: Setting cookie without consent
 */
function setTrackingCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = 'expires=' + date.toUTCString();
    document.cookie = name + '=' + value + ';' + expires + ';path=/';
}

// Initialize tracking and set interval for flushing queue
setTrackingCookie('user_id', generateRandomId(), 365);
setInterval(flushAnalyticsQueue, analyticsConfig.flushInterval);

/**
 * Generate a random ID for tracking
 */
function generateRandomId() {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
}

// Example usage
document.addEventListener('DOMContentLoaded', function() {
    // Track page view when page loads
    logUserActivity('127.0.0.1', {
        action: 'page_view',
        page: window.location.pathname,
        duration: 0
    });
    
    // Track clicks on buttons
    document.querySelectorAll('button').forEach(function(button) {
        button.addEventListener('click', function() {
            logUserActivity('127.0.0.1', {
                action: 'button_click',
                page: window.location.pathname,
                duration: 0
            });
        });
    });
}); 