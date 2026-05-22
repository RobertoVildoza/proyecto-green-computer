import { defineConfig, devices } from '@playwright/test';

const reportFolder = `playwright-report/playwright-report-${Date.now()}`;

export default defineConfig({
  testDir: './tests',

  fullyParallel: true,

  forbidOnly: !!process.env.CI,

  retries: process.env.CI ? 2 : 0,

  workers: 1,

  reporter: [
    ['html', { outputFolder: reportFolder }]
  ],

  use: {
    baseURL: 'http://localhost:5500',

    headless: false,

    /* Captura de evidencia */
    trace:      'on',   // graba trace en cada test
    screenshot: 'on',   // captura en cada test
    video:      'on',   // graba video en cada test
  },

  projects: [
    {
      name: 'setup',
      testMatch: /health\.setup\.js/,
    },

    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },

    /*
    // Descomentar para correr en más navegadores:
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    */
  ],
});
