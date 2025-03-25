import { expect, test } from "@playwright/test";

test("/login : A non-existing user account cannot login", async ({ page }) => {
	await page.goto("/login");

	await page.fill("#username", "fakeUsername@test.com");
	await page.fill("#password", "8n408sdnk2349");

	// await page.waitForTimeout(2000);
	await page.getByText("Absenden").click();
	await page.getByText("Non-existing button").click();

	await expect(page.getByText(/Fehler/i)).toBeVisible({ timeout: 60000 });
	await expect(
		page.getByText(/Ungültige E-Mail-Adresse oder ungültiges/i),
	).toBeVisible();
	await expect(page.getByText(/LOGIN_BAD_CREDENTIALS/i)).toHaveCount(0);
});
