// test_ui.js

const { chromium } = require('playwright');

(async () => {
  // Launch browser
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Navigate to the product list page
  await page.goto('http://localhost:3000/products');

  // Check if the product list is displayed
  const productListTitle = await page.textContent('h2');
  expect(productListTitle).toBe('Product List');

  // Check if at least one product is displayed
  const productItems = await page.$$('li');
  expect(productItems.length).toBeGreaterThan(0);

  // Navigate to the category list page
  await page.goto('http://localhost:3000/categories');

  // Check if the category list is displayed
  const categoryListTitle = await page.textContent('h2');
  expect(categoryListTitle).toBe('Categories');

  // Check if at least one category is displayed
  const categoryItems = await page.$$('li');
  expect(categoryItems.length).toBeGreaterThan(0);

  // Close browser
  await browser.close();
})();

function expect(value) {
  return {
    toBe: (expected) => {
      if (value !== expected) {
        throw new Error(`Expected ${expected}, but got ${value}`);
      }
    },
    toBeGreaterThan: (expected) => {
      if (value <= expected) {
        throw new Error(`Expected value greater than ${expected}, but got ${value}`);
      }
    }
  };
}
