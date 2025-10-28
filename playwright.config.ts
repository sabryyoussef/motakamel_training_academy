import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.PW_BASE_URL || 'http://localhost:3000';

export default defineConfig({
  timeout: 30_000,
  use: { 
    baseURL, 
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    { 
      name: 'chromium', 
      use: { ...devices['Desktop Chrome'] } 
    },
    { 
      name: 'firefox',  
      use: { ...devices['Desktop Firefox'] } 
    },
    { 
      name: 'webkit',   
      use: { ...devices['Desktop Safari'] } 
    }
  ],
  reporter: [
    ['list'], 
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  outputDir: 'test-results/',
  globalSetup: require.resolve('./tests/global-setup.ts'),
  globalTeardown: require.resolve('./tests/global-teardown.ts')
});
