import { defineConfig, devices } from '@playwright/test';

/**
 * Dhanvantari E2E test config.
 * Run against: docker-compose (frontend:3747 + backend:8747)
 *   or: PLAYWRIGHT_BASE_URL=https://dhanvantari.onrender.com npx playwright test
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3747',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* Start docker-compose stack if running locally */
  // webServer: {
  //   command: 'docker compose up',
  //   url: 'http://localhost:3747',
  //   reuseExistingServer: true,
  //   timeout: 120_000,
  // },
});
