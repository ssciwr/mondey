import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/admin - Questions on Children : New question can be added, and appears on the create child form", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");

	const childQuestionText = "Lieblings Tier Farbe";

	await page.waitForTimeout(1000);

	await page.getByRole("link", { name: "Administration" }).click();
	await page.locator('button:has-text("Fragen über Kind")').click();
	await expect(page.getByText(childQuestionText)).not.toBeVisible();

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

	await page.getByText("Kinder").click();
	await page.locator('h5:has-text("+ Neu")').click();
	await modalLoad(page);
	const element_when_adding = page.getByText(childQuestionText);
	await expect(element_when_adding).toBeTruthy();
});
