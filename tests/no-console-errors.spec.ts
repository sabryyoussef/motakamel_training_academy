import { test, expect } from '@playwright/test';

test.describe('Console Error Detection', () => {
  test('no console/page errors', async ({ page, baseURL }) => {
    const logs: { type: string; text: string; timestamp: number }[] = [];
    
    // Capture console messages
    page.on('console', message => {
      logs.push({ 
        type: message.type(), 
        text: message.text(),
        timestamp: Date.now()
      });
    });
    
    // Capture page errors
    page.on('pageerror', error => {
      logs.push({ 
        type: 'pageerror', 
        text: error.message,
        timestamp: Date.now()
      });
    });
    
    // Capture unhandled promise rejections
    page.on('unhandledrejection', error => {
      logs.push({ 
        type: 'unhandledrejection', 
        text: error,
        timestamp: Date.now()
      });
    });

    // Navigate to the page
    await page.goto(baseURL!, { waitUntil: 'load' });
    
    // Wait a bit for any async errors to surface
    await page.waitForTimeout(2000);

    // Filter for error-level messages
    const offenders = logs.filter(log => 
      ['error', 'assert', 'pageerror', 'unhandledrejection'].includes(log.type)
    );

    // Log all captured messages for debugging
    console.log('All captured logs:', JSON.stringify(logs, null, 2));
    
    // Assert no errors
    expect(offenders, `Found ${offenders.length} console/page errors:\n${JSON.stringify(offenders, null, 2)}`).toEqual([]);
  });

  test('network errors detection', async ({ page, baseURL }) => {
    const networkErrors: { url: string; status: number; error: string }[] = [];
    
    page.on('response', response => {
      if (!response.ok()) {
        networkErrors.push({
          url: response.url(),
          status: response.status(),
          error: response.statusText()
        });
      }
    });

    await page.goto(baseURL!, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    expect(networkErrors, `Found ${networkErrors.length} network errors:\n${JSON.stringify(networkErrors, null, 2)}`).toEqual([]);
  });

  test('performance metrics', async ({ page, baseURL }) => {
    await page.goto(baseURL!, { waitUntil: 'load' });
    
    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
      };
    });

    console.log('Performance metrics:', metrics);
    
    // Basic performance assertions
    expect(metrics.loadTime).toBeLessThan(5000); // 5 seconds max load time
    expect(metrics.domContentLoaded).toBeLessThan(2000); // 2 seconds max DOM ready
  });
});
