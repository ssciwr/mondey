import { expect, test } from "@playwright/test";

test("frontpage", async ({ page }) => {
	await page.goto("/");
	await expect(page).toHaveTitle(/mondey/i);
});
