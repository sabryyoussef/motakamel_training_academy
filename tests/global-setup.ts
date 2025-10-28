import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting Playwright test suite...');
  console.log(`📊 Base URL: ${process.env.PW_BASE_URL || 'http://localhost:3000'}`);
  console.log(`🌐 Projects: ${config.projects.map(p => p.name).join(', ')}`);
}

export default globalSetup;
