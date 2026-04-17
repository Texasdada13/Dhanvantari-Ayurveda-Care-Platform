import { test, expect } from '@playwright/test';

const API = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8747';

test.describe('Authentication', () => {
  test('login page renders', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByPlaceholder(/email/i)).toBeVisible();
    await expect(page.getByPlaceholder(/password/i)).toBeVisible();
  });

  test('login with demo credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder(/email/i).fill('demo@dhanvantari.app');
    await page.getByPlaceholder(/password/i).fill('demo1234');
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard/, { timeout: 15000 });
    // Dashboard should show practitioner name or greeting
    await expect(page.locator('body')).toContainText(/dashboard|welcome|patients/i);
  });

  test('login with bad credentials shows error', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder(/email/i).fill('wrong@example.com');
    await page.getByPlaceholder(/password/i).fill('badpassword');
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();

    // Should stay on login page with error
    await expect(page.locator('body')).toContainText(/invalid|error|incorrect/i, { timeout: 5000 });
  });

  test('unauthenticated user redirected from dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    // Should redirect to login
    await expect(page).toHaveURL(/login/, { timeout: 10000 });
  });
});
