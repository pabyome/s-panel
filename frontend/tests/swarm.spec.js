import { test, expect } from '@playwright/test';

test.describe('Docker Swarm Layout', () => {
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

    await page.route('**/api/v1/swarm/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
            "cpu_percent": 15.5,
            "memory": {"total": 8000000000, "used": 4000000000, "percent": 50},
            "containers": {"total": 5, "running": 1}
        }),
      });
    });

    await page.route('**/api/v1/swarm/info', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
            "active": true,
            "is_manager": true,
            "nodes": 3,
            "managers": 1,
            "cluster_id": "abc12345"
        }),
      });
    });

    await page.route('**/api/v1/swarm/nodes', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
              { id: "1", hostname: "node-1", role: "manager", status: "ready", availability: "active" }
          ]),
        });
      });

    await page.route('**/api/v1/swarm/services', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
            { id: "s1", name: "web-service", image: "nginx:latest", replicas: 3, mode: { Replicated: {} } }
        ]),
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

  test('should display overview tab correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/docker/overview');

    // Check Tabs
    await expect(page.getByRole('link', { name: 'Overview' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Container' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Swarm' })).toBeVisible();

    // Check Stats
    await expect(page.getByText('CPU usage')).toBeVisible();
    await expect(page.getByText('15.5 %')).toBeVisible();

    // Check Container Grid
    await expect(page.getByText('test_container')).toBeVisible();
  });

  test('should navigate to swarm tab and show info', async ({ page }) => {
    await page.goto('http://localhost:5173/docker/overview');

    await page.getByRole('link', { name: 'Swarm' }).click();

    await expect(page.getByRole('heading', { name: 'Swarm Management' })).toBeVisible();
    await expect(page.getByText('Cluster ID')).toBeVisible();
    await expect(page.getByText('abc12345')).toBeVisible();

    // Check Nodes Table
    await expect(page.getByText('node-1')).toBeVisible();

    // Check Services Table
    await expect(page.getByText('web-service')).toBeVisible();

    await page.screenshot({ path: 'swarm_layout.png' });
  });
});
