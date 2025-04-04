import { type Page, expect, test } from "@playwright/test";
import { login } from "./utils";

test("/login : A non-existing user account cannot login", async ({ page }) => {
	await login(page, "fakeUsername@test.com", "8n408sdnk2349");
	await expect(page.getByText(/Fehler/i)).toBeVisible();
	await expect(
		page.getByText(/Ungültige E-Mail-Adresse oder ungültiges/i),
	).toBeVisible();
	await expect(page.getByText(/LOGIN_BAD_CREDENTIALS/i)).toHaveCount(0);
});

test("/login : login as valid user", async ({ page, isMobile }) => {
	await login(page, "user@mondey.de", "user");
	if (!isMobile) {
		await expect(page.getByText(/user@mondey.de/i)).toBeVisible();
		await expect(page.getByText(/Research/i)).toHaveCount(0);
		await expect(page.getByText(/Admin/i)).toHaveCount(0);
	}
	await expect(page.getByText(/userChild1/i)).toBeVisible();
});

test("/login : login as valid researcher", async ({ page, isMobile }) => {
	await login(page, "researcher@mondey.de", "researcher");
	if (!isMobile) {
		await expect(page.getByText(/researcher@mondey.de/i)).toBeVisible();
		await expect(page.getByText(/Research/i)).toBeVisible();
		await expect(page.getByText(/Admin/i)).toHaveCount(0);
	}
});

test("/login : login as valid admin", async ({ page, isMobile }) => {
	await login(page, "admin@mondey.de", "admin");
	if (!isMobile) {
		await expect(page.getByText(/admin@mondey.de/i)).toBeVisible();
		await expect(page.getByText(/Research/i)).toHaveCount(0);
		await expect(page.getByText(/Admin/i)).toBeVisible();
	}
});
