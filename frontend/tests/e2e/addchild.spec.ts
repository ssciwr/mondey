import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/children/gallery - Can add Child", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await page.getByText("Kinder").first().click();
	await page.locator('h5:has-text("+ Neu")').click();
	await modalLoad(page);
	const element_when_adding = page.getByText("Name des Kindes?");
	await expect(element_when_adding).toBeTruthy();
});
