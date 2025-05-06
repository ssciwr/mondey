import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("/userLand/admin - Questions on Children : New child question can be added, and appears on the create child form", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await expect(
		page.getByText("Wählen sie ein Kind zur Beobachtung aus"),
	).toBeVisible();

	// add a new child question in the admin interface
	if (isMobile) {
		await page.getByTestId("mobile-userland-navbar").click(); // open the sidebar.
	}
	await page.getByRole("link", { name: "Administration" }).click();
	await page.locator('button:has-text("Fragen über Kind")').click();

	const childQuestionText = `question-${crypto.randomUUID()}`;

	await page.locator('button:has-text("Hinzufügen")').click();
	await page.getByTestId("text-question-input-de").fill(childQuestionText);
	await page.getByTestId("visibility-checkbox").setChecked(true);

	await page.getByTestId("questionTypeSelect").click();
	await page.selectOption('[data-testid="questionTypeSelect"]', {
		label: "Text",
	});

	await page.locator('button:has-text("Änderungen speichern")').click();
	await expect(page.getByText("Fragen über Kind")).toHaveCount(2);
	await expect(page.getByText(childQuestionText)).toBeVisible();

	// go to child gallery to see new question
	await page.goto("/userLand/children/gallery");
	await page.locator('h5:has-text("+ Neu")').click();
	await expect(page.getByText(childQuestionText)).toBeVisible();
});
