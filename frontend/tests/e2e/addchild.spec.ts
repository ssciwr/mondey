import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("/userLand/children - Can add Child", async ({ page, isMobile }) => {
	await login(page, "admin@mondey.de", "admin");
	await page.locator('h5:has-text("+ Neu")').click();
	const element_when_adding = page.getByText("Name des Kindes?");
	await expect(element_when_adding).toBeVisible();
});
