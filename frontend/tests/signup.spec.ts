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

test("/login : A non-existing user account cannot login", async ({ page }) => {
	await page.goto("/login");

	await page.fill("#username", "fakeUsername@test.com");
	await page.fill("#password", "8n408sdnk2349");

	await page.getByText("Absenden").click();

	await expect(page.getByText(/Fehler/i)).toBeVisible({ timeout: 15000 });
	await expect(
		page.getByText(/Ungültige E-Mail-Adresse oder ungültiges/i),
	).toBeVisible();
	await expect(page.getByText(/LOGIN_BAD_CREDENTIALS/i)).toHaveCount(0);
});
