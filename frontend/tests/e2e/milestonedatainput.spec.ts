import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/children/gallery - Can add Child", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");
	
	// Create a new child so existing milestone data isn't affected
	await page.locator('h5:has-text("Neu")').click();
	await modalLoad(page);

	await page.locator('input[for="Name des Kindes?"]').fill("Test Child");
	await page.locator('input[for="Geburtsjahr des Kindes?"]').fill("2020");
	await page.locator('input[for="Geburtsmonat des Kindes?"]').fill("6");
	await page.getByRole("button", { name: "Speichern" }).click();

	await page.waitForTimeout(1000);
	
	// Click on the child's name
	await page.getByText("Test Child").click();
	
	// Navigate to milestones
	await page.getByRole("button", { name: "Weiter zu Meilensteinen" }).click();
	
	// Select milestone group "Reading skills"
	await page.locator('h5:has-text("Reading skills")').click();
	
	// Select specific milestone "Recognizes Digits"
	await page.locator('h5:has-text("Recognizes Digits")').click();
	
	// Verify milestone content is visible
	await expect(page.getByText("Recognizes Digits")).toBeVisible();
	// You would add the description verification here with the actual text
	await expect(page.getByText(/description/)).toBeVisible();
	
	// Select answer "Weitgehend"
	await page.getByRole("button", { name: "Weitgehend" }).click();
});
