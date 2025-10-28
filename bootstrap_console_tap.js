/**
 * Bootstrap Console Tap Client
 * 
 * This script captures console errors, unhandled rejections, and window errors
 * and sends them to the console tap server for centralized logging.
 * 
 * Works in Chrome, Edge, Firefox, and Safari.
 * No debugger dependency required.
 */

(function () {
  'use strict';
  
  // Configuration
  const CONFIG = {
    tapPort: window.__CONSOLE_TAP_PORT__ || 5055,
    tapUrl: window.__CONSOLE_TAP_URL__,
    enabled: window.__CONSOLE_TAP_ENABLED__ !== false,
    batchSize: 10,
    flushInterval: 5000
  };

  if (!CONFIG.enabled) {
    console.log('[Console Tap] Disabled');
    return;
  }

  // Build endpoint URL
  let endpoint;
  if (CONFIG.tapUrl) {
    endpoint = CONFIG.tapUrl;
  } else {
    const origin = location.origin.replace(/:\d+$/, `:${CONFIG.tapPort}`);
    endpoint = `${origin}/__console_tap__`;
  }

  // Message queue for batching
  let messageQueue = [];
  let flushTimer = null;

  // Send messages to server
  function post(data) {
    try {
      const payload = JSON.stringify({
        ...data,
        url: location.href,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
        sessionId: getSessionId()
      });

      if (navigator.sendBeacon) {
        navigator.sendBeacon(endpoint, new Blob([payload], { type: 'application/json' }));
      } else {
        fetch(endpoint, { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' }, 
          body: payload, 
          keepalive: true 
        }).catch(() => {
          // Silently fail if server is not available
        });
      }
    } catch (e) {
      // Silently fail
    }
  }

  // Batch messages for efficiency
  function queueMessage(data) {
    messageQueue.push(data);
    
    if (messageQueue.length >= CONFIG.batchSize) {
      flushMessages();
    } else if (!flushTimer) {
      flushTimer = setTimeout(flushMessages, CONFIG.flushInterval);
    }
  }

  function flushMessages() {
    if (messageQueue.length === 0) return;
    
    post({
      msg: 'batch',
      messages: messageQueue,
      count: messageQueue.length
    });
    
    messageQueue = [];
    if (flushTimer) {
      clearTimeout(flushTimer);
      flushTimer = null;
    }
  }

  // Generate session ID
  function getSessionId() {
    if (!window.__CONSOLE_TAP_SESSION_ID__) {
      window.__CONSOLE_TAP_SESSION_ID__ = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    return window.__CONSOLE_TAP_SESSION_ID__;
  }

  // Capture window errors
  window.addEventListener('error', function (e) {
    queueMessage({
      msg: 'window.error',
      message: e.message,
      stack: e.error?.stack,
      source: e.filename,
      line: e.lineno,
      col: e.colno,
      level: 'error'
    });
  });

  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', function (e) {
    const reason = e.reason || {};
    queueMessage({
      msg: 'unhandledrejection',
      reason: String(reason?.message || reason),
      stack: reason?.stack,
      level: 'error'
    });
  });

  // Capture console methods
  const originalMethods = {
    error: console.error,
    warn: console.warn,
    info: console.info,
    log: console.log,
    debug: console.debug
  };

  Object.keys(originalMethods).forEach(method => {
    console[method] = function (...args) {
      // Call original method
      originalMethods[method].apply(console, args);
      
      // Send to tap server
      queueMessage({
        msg: `console.${method}`,
        args: args.map(a => {
          if (typeof a === 'string') return a;
          if (a instanceof Error) return { message: a.message, stack: a.stack };
          try {
            return JSON.stringify(a);
          } catch {
            return String(a);
          }
        }),
        level: method === 'error' ? 'error' : method === 'warn' ? 'warn' : 'info'
      });
    };
  });

  // Capture performance issues
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver(function (list) {
        list.getEntries().forEach(function (entry) {
          if (entry.entryType === 'navigation' && entry.loadEventEnd - entry.loadEventStart > 3000) {
            queueMessage({
              msg: 'performance.slow_load',
              loadTime: entry.loadEventEnd - entry.loadEventStart,
              level: 'warn'
            });
          }
        });
      });
      observer.observe({ entryTypes: ['navigation'] });
    } catch (e) {
      // PerformanceObserver not supported
    }
  }

  // Flush messages on page unload
  window.addEventListener('beforeunload', flushMessages);
  window.addEventListener('pagehide', flushMessages);

  // Initialize
  queueMessage({
    msg: 'console_tap_initialized',
    config: CONFIG,
    level: 'info'
  });

  console.log('[Console Tap] Initialized and monitoring console errors');
})();
