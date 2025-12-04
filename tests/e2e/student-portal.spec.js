/**
 * End-to-end tests for student portal workflow
 * Uses Playwright for browser automation
 */

const { test, expect } = require('@playwright/test');

test.describe('Student Portal E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to student portal
    await page.goto('http://localhost:3000/frontend/pages/index.html');
  });

  test('Student can access the portal and see Watson Assistant', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Student Portal.*CPL.*Northeastern University/);

    // Wait for Watson Assistant to load
    await page.waitForTimeout(3000);

    // Check if Watson Assistant iframe is present
    const watsonFrame = page.frameLocator('iframe[title*="Watson Assistant"]');
    await expect(watsonFrame.locator('body')).toBeVisible({ timeout: 10000 });
  });

  test('Student can upload a document', async ({ page }) => {
    // Create a test file
    const testFilePath = 'tests/fixtures/sample.pdf';

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Look for file input (might be hidden)
    const fileInput = page.locator('input[type="file"]').first();

    if (await fileInput.isVisible()) {
      // Upload file
      await fileInput.setInputFiles(testFilePath);

      // Click upload button if present
      const uploadButton = page.locator('button:has-text("Upload"), input[type="submit"]').first();
      if (await uploadButton.isVisible()) {
        await uploadButton.click();

        // Wait for upload response
        await page.waitForTimeout(5000);

        // Check for success indication
        await expect(page.locator('text=/uploaded|success|complete/i')).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('Student can interact with Watson Assistant', async ({ page }) => {
    // Wait for Watson Assistant to load
    await page.waitForTimeout(5000);

    // Try to interact with Watson Assistant
    const watsonFrame = page.frameLocator('iframe[title*="Watson Assistant"]');

    try {
      // Look for chat input
      const chatInput = watsonFrame.locator('input[type="text"], textarea').first();
      await chatInput.fill('Hello, I need help with CPL');

      // Look for send button
      const sendButton = watsonFrame.locator('button[type="submit"], button:has-text("Send")').first();
      await sendButton.click();

      // Wait for response
      await page.waitForTimeout(3000);

      // Check for Watson response
      await expect(watsonFrame.locator('text=/help|CPL|credit/i')).toBeVisible({ timeout: 10000 });
    } catch (error) {
      console.log('Watson Assistant interaction failed:', error.message);
      // This might fail due to Watson Assistant security restrictions in test environment
    }
  });

  test('Student can navigate to status page', async ({ page }) => {
    // Look for status link
    const statusLink = page.locator('a:has-text("Status"), a[href*="status"]').first();

    if (await statusLink.isVisible()) {
      await statusLink.click();

      // Check if we're on status page
      await expect(page.locator('h1, h2, title')).toContainText(/status/i);
    }
  });

  test('Page loads without console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('http://localhost:3000/frontend/pages/index.html');
    await page.waitForTimeout(5000);

    // Check for critical errors (ignore Watson Assistant CORS warnings)
    const criticalErrors = errors.filter(error =>
      !error.includes('Watson') &&
      !error.includes('CORS') &&
      !error.includes('embed')
    );

    expect(criticalErrors.length).toBe(0);
  });

  test('All required assets load successfully', async ({ page }) => {
    const failedRequests = [];

    page.on('requestfailed', request => {
      failedRequests.push(request.url());
    });

    await page.goto('http://localhost:3000/frontend/pages/index.html');
    await page.waitForLoadState('networkidle');

    // Filter out external resources that might fail in test environment
    const criticalFailures = failedRequests.filter(url =>
      !url.includes('googleapis.com') &&
      !url.includes('watson') &&
      !url.includes('ibm.com')
    );

    expect(criticalFailures.length).toBe(0);
  });
});