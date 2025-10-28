(function () {
  'use strict';
  
  // Configuration
  const CONSOLE_TAP_PORT = window.__CONSOLE_TAP_PORT__ || 5055;
  const CONSOLE_TAP_URL = window.__CONSOLE_TAP_URL__ || `${location.protocol}//${location.hostname}:${CONSOLE_TAP_PORT}/__console_tap__`;
  
  // Utility function to safely stringify objects
  function safeStringify(obj) {
    try {
      return JSON.stringify(obj);
    } catch (e) {
      return String(obj);
    }
  }
  
  // Send data to console tap server
  function post(data) {
    try {
      const payload = JSON.stringify({
        ...data,
        timestamp: Date.now(),
        url: location.href,
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      });
      
      if (navigator.sendBeacon) {
        navigator.sendBeacon(CONSOLE_TAP_URL, new Blob([payload], { type: 'application/json' }));
      } else {
        fetch(CONSOLE_TAP_URL, { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' }, 
          body: payload, 
          keepalive: true 
        }).catch(() => {}); // Silent fail
      }
    } catch (e) {
      // Silent fail - don't break the app
    }
  }
  
  // Capture window errors
  window.addEventListener('error', function(e) {
    post({
      level: 'error',
      type: 'window.error',
      message: e.message,
      filename: e.filename,
      lineno: e.lineno,
      colno: e.colno,
      stack: e.error ? e.error.stack : null
    });
  });
  
  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', function(e) {
    const reason = e.reason || {};
    post({
      level: 'error',
      type: 'unhandledrejection',
      reason: String(reason.message || reason),
      stack: reason.stack || null
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
  
  Object.keys(originalMethods).forEach(function(method) {
    console[method] = function() {
      // Call original method
      originalMethods[method].apply(console, arguments);
      
      // Send to tap server
      post({
        level: method,
        type: 'console.' + method,
        args: Array.prototype.slice.call(arguments).map(function(arg) {
          return typeof arg === 'string' ? arg : safeStringify(arg);
        })
      });
    };
  });
  
  // Capture network errors (if fetch is available)
  if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function() {
      return originalFetch.apply(this, arguments)
        .catch(function(error) {
          post({
            level: 'error',
            type: 'fetch.error',
            message: error.message,
            stack: error.stack
          });
          throw error;
        });
    };
  }
  
  // Send initialization message
  post({
    level: 'info',
    type: 'console_tap.initialized',
    message: 'Console tap initialized'
  });
  
})();
