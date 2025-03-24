import { expect, test } from "@playwright/test";

[
	{ code: "", red: false },
	{ code: "123451", red: false },
	{ code: "666666", red: true },
	{ code: "xyz", red: true },
].forEach(({ code, red }) => {
	test(`/signup/${code} : research code input is ${red ? "" : "not"} red`, async ({
		page,
	}) => {
		await page.goto(`/signup/${code}`);
		const input = page.getByTestId("researchCodeInput");
		await expect(input).toHaveValue(code);
		if (red) {
			await expect(input).toHaveClass(/text-red/);
		} else {
			await expect(input).not.toHaveClass(/text-red/);
		}
		await expect(page.locator("[type=submit]")).toBeDisabled();
	});
});

/*
test("/ : A non-existing user account cannot login", async ({ page }) => {
	await page.goto("/login");

	const isLoggedIn = await page.evaluate(async () => {
		const { user } = await import("$lib/stores/userStore.svelte");
		if (user.data === null) {
			await user.load();
		}
		return user.data !== null;
	});
	expect(isLoggedIn).toBeTruthy();
});
*/
