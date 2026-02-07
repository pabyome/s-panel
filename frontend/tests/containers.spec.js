import { test, expect } from '@playwright/test';

test.describe('Containers View', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/v1/containers/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
            {
                "id": "123",
                "short_id": "12",
                "name": "test_container",
                "image": "nginx:latest",
                "status": "running",
                "state": {"Status": "running"},
                "ports": {"80/tcp": [{"HostPort": "8080"}]},
                "created": "2023-01-01"
            }
        ]),
      });
    });

    await page.route('**/api/v1/containers/*/logs?tail=200', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ logs: "Test logs content" }),
      });
    });

    // Mock auth user
    await page.route('**/api/v1/auth/me', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ username: 'admin', role: 'admin' })
        });
    });

    // Set token
    await page.addInitScript(() => {
        window.localStorage.setItem('token', 'fake-jwt-token');
    });
  });

  test('should display container list', async ({ page }) => {
    await page.goto('http://localhost:5173/containers');

    // Check header
    await expect(page.getByRole('heading', { name: 'Containers' })).toBeVisible();

    // Check container in table
    await expect(page.getByText('test_container')).toBeVisible();
    await expect(page.getByText('nginx:latest')).toBeVisible();
    await expect(page.getByText('running', { exact: true })).toBeVisible();

    // Check actions
    await expect(page.getByTitle('Stop')).toBeVisible();
    await expect(page.getByTitle('Restart')).toBeVisible();
    await expect(page.getByTitle('Logs')).toBeVisible();

    await page.screenshot({ path: 'containers.png' });
  });

  test('should show logs modal', async ({ page }) => {
    await page.goto('http://localhost:5173/containers');

    await page.getByTitle('Logs').click();

    await expect(page.getByText('Logs: test_container')).toBeVisible();
    await expect(page.getByText('Test logs content')).toBeVisible();

    await page.getByRole('button', { name: 'Close' }).click();
    await expect(page.getByText('Logs: test_container')).not.toBeVisible();
  });

  test('should open run container modal and show fields', async ({ page }) => {
    await page.goto('http://localhost:5173/containers');

    await page.getByRole('button', { name: 'Run Container' }).click();

    await expect(page.getByRole('heading', { name: 'Run New Container' })).toBeVisible();
    await expect(page.getByLabel('Image')).toBeVisible();
    await expect(page.getByLabel('Name (Optional)')).toBeVisible();

    // Check Env Vars
    await expect(page.getByText('Environment Variables')).toBeVisible();
    await page.getByRole('button', { name: 'Add Variable' }).click();
    await expect(page.getByPlaceholder('KEY')).toBeVisible();

    // Check Volumes
    await expect(page.getByText('Volumes')).toBeVisible();
    await page.getByRole('button', { name: 'Add Volume' }).click();
    await expect(page.getByPlaceholder('/host/path')).toBeVisible();

    await page.screenshot({ path: 'containers_modal.png' });

    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('heading', { name: 'Run New Container' })).not.toBeVisible();
  });
});
