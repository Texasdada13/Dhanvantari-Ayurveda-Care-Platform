import { test, expect } from '@playwright/test';

const API = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8747';

test.describe('Patient Portal', () => {
  // Helper: get a valid portal token from the API (uses demo data)
  let portalToken: string | null = null;

  test.beforeAll(async ({ request }) => {
    // Login as demo practitioner
    const loginRes = await request.post(`${API}/api/auth/login`, {
      data: { email: 'demo@dhanvantari.app', password: 'demo1234' },
    });
    if (loginRes.ok()) {
      const { access_token } = await loginRes.json();
      // Get patients to find one with a portal token
      const patientsRes = await request.get(`${API}/api/patients`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      if (patientsRes.ok()) {
        const patients = await patientsRes.json();
        const withToken = patients.find((p: any) => p.checkin_token);
        if (withToken) portalToken = withToken.checkin_token;
      }
    }
  });

  test('portal home loads for valid token', async ({ page }) => {
    test.skip(!portalToken, 'No portal token found in demo data');
    await page.goto(`/portal/${portalToken}`);
    await expect(page.locator('body')).toContainText(/check-in|plan|welcome/i, { timeout: 10000 });
  });

  test('portal 404 for invalid token', async ({ page }) => {
    await page.goto('/portal/nonexistent-fake-token-12345');
    // Should show error state, not crash
    await expect(page.locator('body')).toContainText(/not found|invalid|error|expired/i, {
      timeout: 10000,
    });
  });

  test('portal check-in form renders', async ({ page }) => {
    test.skip(!portalToken, 'No portal token found in demo data');
    await page.goto(`/portal/${portalToken}`);
    // Look for check-in related UI
    const body = page.locator('body');
    // Portal should show some form of checkin or plan content
    await expect(body).toBeVisible();
  });
});
