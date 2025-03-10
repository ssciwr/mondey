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
	await expect(page.getByText(`${i18n.tr.settings.settings}`)).toBeVisible();
	await expect(page.getByText(`${i18n.tr.settings.changeEmail}`)).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.settings.newEmail}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.settings.newEmailConfirm}`),
	).toBeVisible();

	await expect(
		page.getByText(`${i18n.tr.settings.changePassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.settings.oldPassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.settings.newPassword}`),
	).toBeVisible();
	await expect(
		page.getByPlaceholder(`${i18n.tr.settings.newPasswordConfirm}`),
	).toBeVisible();
});

test("usersettings_emails-do-not-match", async ({ page }) => {
	await page.getByPlaceholder(`${i18n.tr.settings.newEmail}`).fill("e@mail.de");
	await page
		.getByPlaceholder(`${i18n.tr.settings.newEmailConfirm}`)
		.fill("e.unequalmail.de");
	await page.locator("#changeEmailSubmitButton").click();
	await expect(page.locator("#alertMessage_settings")).toBeVisible();
	await expect(page.locator("#alertMessage_settings").textContent()).toBe(
		`${i18n.tr.settings.emailsDontMatch}`,
	);
});

test("usersettings_emails-are-empty", async ({ page }) => {
	await page.getByPlaceholder(`${i18n.tr.settings.newEmail}`).fill("");
	await page
		.getByPlaceholder(`${i18n.tr.settings.newEmailConfirm}`)
		.fill("a@b.com");
	await page.locator("#changeEmailSubmitButton").click();
	await expect(page.locator("#alertMessage_settings")).toBeVisible();
	await expect(page.locator("#alertMessage_settings").textContent()).toBe(
		`${i18n.tr.settings.emailEmpty}`,
	);
});

test("usersettings_successful-email-update", async ({ page }) => {
	// TODO
});

test("usersettings_error-on-email-update", async ({ page }) => {
	// TODO
});

test("usersettings_password-do-not-match", async ({ page }) => {
	await page.getByPlaceholder(`${i18n.tr.settings.newEmail}`).fill("123");
	await page
		.getByPlaceholder(`${i18n.tr.settings.newEmailConfirm}`)
		.fill("456");
	await page.locator("#changeEmailSubmitButton").click();
	await expect(page.locator("#alertMessage_settings")).toBeVisible();
	await expect(page.locator("#alertMessage_settings").textContent()).toBe(
		`${i18n.tr.settings.passwordEmpty}`,
	);
});

test("usersettings_password-are-empty", async ({ page }) => {
	await page.getByPlaceholder(`${i18n.tr.settings.newEmail}`).fill("");
	await page
		.getByPlaceholder(`${i18n.tr.settings.newEmailConfirm}`)
		.fill("45667");
	await page.locator("#changeEmailSubmitButton").click();
	await expect(page.locator("#alertMessage_settings")).toBeVisible();
	await expect(page.locator("#alertMessage_settings").textContent()).toBe(
		`${i18n.tr.settings.passwordsDontMatch}`,
	);
});

test("usersettings_successful-password-update", async ({ page }) => {
	// TODO
});

test("usersettings_error-on-password-update", async ({ page }) => {
	// TODO
});
