import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('✅ Playwright test suite completed');
  console.log(`📁 Results saved to: ${config.outputDir}`);
}
