import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig, devices } from '@playwright/test';

// The UI proxies /api to API_URL (default http://localhost:5000). When the repo's Python
// virtualenv is present (local development), start the FastAPI backend too so
// `npm run test:e2e` exercises the whole stack on its own. In the Playwright container
// there is no venv and the API is a separate service, so only the frontend is started.
const repoRoot = resolve(__dirname, '..');
const uvicorn = resolve(repoRoot, '.venv', 'bin', 'uvicorn');
const apiServer = existsSync(uvicorn)
  ? [
      {
        command: `${uvicorn} backend.api.main:app --port 5000`,
        cwd: repoRoot,
        env: { APP_ENV: 'development' },
        url: 'http://localhost:5000/api/v1/health',
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
    ]
  : [];

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,
  reporter: 'html',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: [
    ...apiServer,
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
  ],
});
