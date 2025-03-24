import { expect, test } from "@playwright/test";

// Could export some kind of "async logInAnonymousTestUser"

test("/ : Anonymous users can log in", async ({ page }) => {
	await page.goto("/");
	const button = page.getByTestId("anonymousLogin");
	await button.click();
	await expect(page).toHaveURL("/userLand/children/gallery");
	await expect(page.getByText("Kinder")).toBeVisible();
	const isLoggedIn = await page.evaluate(async () => {
		const { user } = await import("$lib/stores/userStore.svelte");
		if (user.data === null) {
			await user.load();
		}
		return user.data !== null;
	});
	expect(isLoggedIn).toBeTruthy();
});
