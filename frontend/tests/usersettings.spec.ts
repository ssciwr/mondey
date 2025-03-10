import { i18n } from "$lib/i18n.svelte";
import { expect, test } from "@playwright/test";

test.describe("", () => {
	test.beforeEach(async ({ page }) => {
		// Mock login or authentication
		const mockrequests = [
			{
				url: "**/api/users/me",
				response: { id: 1, email: "current@example.com", name: "Test User" },
			},
		];

		// mock login
		await page.route("/api/login", async (route) => {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({
					url: "**/api/login",
					response: { token: "fake-token" },
				}),
			});
		});

		// navigate to settings page
		await page.goto("/userLand/userLandingpage");
		await page.waitForLoadState("networkidle");

		// go to the right element --> settings
		await page.locator("#settingsTab").click();
		await page.waitForSelector("#settingsTab");
	});
});

test("usersettings_display-settings-form", async ({ page }) => {
	// Check that both forms are present
	await expect(page.getByText(`${i18n.tr.userData.settings}`)).toBeVisible();
	await expect(page.getByText(`${i18n.tr.userData.changeEmail}`)).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.userData.newEmail}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.userData.newEmailConfirm}`),
	).toBeVisible();

	await expect(
		page.getByText(`${i18n.tr.userData.changePassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.userData.oldPassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.userData.newPassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.userData.newPasswordConfirm}`),
	).toBeVisible();
});

test("usersettings_emails-do-not-match", async ({ page }) => {
	// TODO
});

test("usersettings_emails-are-empty", async ({ page }) => {
	// TODO
});

test("usersettings_successful-email-update", async ({ page }) => {
	// TODO
});

test("usersettings_error-on-email-update", async ({ page }) => {
	// TODO
});

test("usersettings_password-do-not-match", async ({ page }) => {
	// TODO
});

test("usersettings_password-are-empty", async ({ page }) => {
	// TODO
});

test("usersettings_successful-password-update", async ({ page }) => {
	// TODO
});

test("usersettings_error-on-password-update", async ({ page }) => {
	// TODO
});
