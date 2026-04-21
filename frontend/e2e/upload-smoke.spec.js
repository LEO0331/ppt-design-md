const { test, expect } = require('@playwright/test');
const path = require('path');

test('uploads sample1.pptx and renders generated design markdown', async ({ page }) => {
  test.setTimeout(180000);
  const samplePath = path.resolve(__dirname, '../../examples/sample1.pptx');

  await page.goto('http://127.0.0.1:4173');
  await page.setInputFiles('#fileInput', samplePath);

  const status = page.locator('#status');
  await expect(status).toContainText('Done.', { timeout: 150000 });

  const editor = page.locator('#designEditor');
  await expect(editor).toHaveValue(/# DESIGN\.md/, { timeout: 150000 });
  await expect(editor).toHaveValue(/Color System/);
});
