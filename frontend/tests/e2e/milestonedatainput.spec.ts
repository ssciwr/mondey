import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("/userLand/children/gallery - Childs Milestone % gets updated when you select it to have been achieved", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");

	// Create a new child so existing milestone data isn't affected
	// and use a unique name for each child to allow tests to run in parallel without affecting each other
	const childName = `child-${crypto.randomUUID()}`;

	await page.locator('h5:has-text("+ Neu")').click();
	await expect(page.getByText("Neues Kind registrieren")).toBeVisible();
	await expect(page.getByText("Name des Kindes?")).toBeVisible();

	await page.locator('input[for="Name des Kindes?"]').fill(childName);
	await page
		.locator('input[for="Geburtsjahr des Kindes?"]')
		.fill((new Date().getFullYear() - 1).toString());
	await page.locator('input[for="Geburtsmonat des Kindes?"]').fill("9");

	// Make sure the button is visible before clicking
	const finishButton = page.getByRole("button", { name: "Abschließen" });
	await finishButton.scrollIntoViewIfNeeded();
	await finishButton.waitFor({ state: "visible" });
	await finishButton.click();

	// Wait until child page has loaded
	await expect(
		page.getByText("Wählen sie ein Kind zur Beobachtung aus"),
	).toBeVisible();

	// Click on the child's name
	await page.getByText(childName).click();

	// Navigate to milestones
	await page.getByRole("button", { name: "Weiter zu Meilensteinen" }).click();

	// Select milestone group "Reading skills"
	await page.locator('h5:has-text("Textlesen")').click();

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
	await page.goto("/userLand/children/gallery", { waitUntil: "networkidle" });

	await page.getByText(childName).click();

	await page.getByRole("button", { name: "Weiter zu Meilensteinen" }).click();

	await expect(page.getByText("25%")).toBeVisible();
});
