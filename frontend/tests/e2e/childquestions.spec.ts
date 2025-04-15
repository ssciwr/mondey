import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/admin - Questions on Children : New child question can be added, and appears on the create child form", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");

	const childQuestionText = "Lieblings Tier Farbe";

	await page.waitForTimeout(1000);

	if (isMobile) {
		await page.getByTestId("mobile-userland-navbar").click(); // open the sidebar.
	}
	await page.getByRole("link", { name: "Administration" }).click();
	await page.locator('button:has-text("Fragen über Kind")').click();

	await page.waitForTimeout(500); // would like to use network idle don't like hardcoding but we need questions to load

	// This hardcoded way I don't like but basically if we use the other approach it seems to use a ref and update
	// so comparisons don't work. But by doing this approach, we freeze the initial count for later comparison.
	const initialQuestions = await page
		.getByText(childQuestionText, { exact: true })
		.count();

	await page.locator('button:has-text("Hinzufügen")').click();
	await modalLoad(page);
	await page.getByTestId("text-question-input-de").fill(childQuestionText);

	await page.getByTestId("questionTypeSelect").click();
	await page.selectOption('[data-testid="questionTypeSelect"]', {
		label: "Text",
	});

	await page.locator('button:has-text("Änderungen speichern")').click();
	await page.waitForTimeout(1000);
	const element = page.getByText(childQuestionText);
	await expect(element).toBeTruthy();

	await page.goto("/userLand/children/gallery");
	await page.locator('h5:has-text("+ Neu")').click();
	await modalLoad(page);
	const element_when_adding = page.getByText(childQuestionText).all();
	await expect(element_when_adding).toBeTruthy();

	if (isMobile) {
		await page.getByTestId("mobile-userland-navbar").click(); // open the sidebar.
	}
	await page.getByRole("link", { name: "Administration" }).click();
	await page.locator('button:has-text("Fragen über Kind")').click();

	// Force a complete reload of the page to avoid any caching issues with # of questions.
	await page.waitForLoadState("networkidle");
	await page.waitForTimeout(3000);

	const laterQuestions = await page
		.getByText(childQuestionText, { exact: true })
		.count();

	// Add some debugging to help troubleshoot
	console.log(
		`Initial count: ${initialQuestions}, Later count: ${laterQuestions}`,
	);

	// Make sure we're comparing the right numbers
	expect(laterQuestions).toBe(initialQuestions + 1);
});
