import { expect, test } from "@playwright/test";

// Could export some kind of "async logInAnonymousTestUser"

test("/ : Anonymous users can log in", async ({ page }) => {
	await page.goto("/", { waitUntil: "networkidle" });
	const button = page.getByTestId("anonymousLogin");
	await button.click();
	await expect(page).toHaveURL("/userLand/children/gallery", {
		timeout: 30000,
	});
	await expect(page.getByRole("heading", { name: "Kinder" })).toBeVisible();
});
