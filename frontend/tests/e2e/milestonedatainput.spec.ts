import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/children/gallery - Can add Child", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");

	// Create a new child so existing milestone data isn't affected
	await page.locator('h5:has-text("+ Neu")').click();
	await modalLoad(page);

	await page.locator('input[for="Name des Kindes?"]').fill("Test Child 2");
	await page
		.locator('input[for="Geburtsjahr des Kindes?"]')
		.fill((new Date().getFullYear() - 1).toString());
	await page.locator('input[for="Geburtsmonat des Kindes?"]').fill("9");
	
	// Make sure the button is visible before clicking
	const finishButton = page.getByRole("button", { name: "Abschließen" });
	await finishButton.scrollIntoViewIfNeeded();
	await finishButton.waitFor({ state: 'visible' });
	await finishButton.click();

	// Wait for navigation to complete
	await page.waitForTimeout(1000);

	// Click on the child's name
	await page.getByText("Test Child 2").last().click(); // really vital that we don't put "first" here
	// or we could just get an outdated child..

	// Navigate to milestones
	await page.getByRole("button", { name: "Weiter zu Meilensteinen" }).click();

	// Select milestone group "Reading skills"
	await page.locator('h5:has-text("Textlesen")').click();
	await page.waitForTimeout(500);

	// Select specific milestone "Recognizes Digits"
	await page.locator('h5:has-text("Formen erkennen")').click();

	// Verify milestone content is visible
	await expect(page.getByText("Formen erkennen")).toBeVisible();
	// You would add the description verification here with the actual text
	await expect(
		page.getByText(
			"Kind kann grundlegende Formen wie Kreise und Quadrate identifizieren",
		),
	).toBeVisible();

	// Select answer "Weitgehend"
	await page.getByRole("button", { name: "Weitgehend" }).click();

	// Part 2: We now check that the actual score was updated from 0 to 25% for the milestone group:
	await page.goto("/userLand/children/gallery");
	await page.waitForTimeout(1000);

	// this line must be the same as the above or we will get a different child...
	await page.getByText("Test Child 2").last().click();

	await page.getByRole("button", { name: "Weiter zu Meilensteinen" }).click();

	await expect(page.getByText("25%")).toBeVisible();
});
