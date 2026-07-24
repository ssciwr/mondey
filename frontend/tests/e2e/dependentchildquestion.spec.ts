import { expect, test } from "@playwright/test";
import { login } from "./utils";

// Creates a "parent" multiple-choice child question and a dependent child
// question that is only shown when the parent is answered with a given value,
// then checks the conditional show/hide + clear-on-hide behaviour on the
// create-child form.
test("/userLand/admin - dependent child question is shown/hidden based on the parent answer and cleared when hidden", async ({
	page,
	isMobile,
}) => {
	test.skip(isMobile, "The admin interface is not covered by mobile E2E tests");

	const unique = crypto.randomUUID().slice(0, 8);
	const parentText = `parent-${unique}`;
	const dependentText = `dependent-${unique}`;
	const triggerValue = `yes-${unique}`;
	const otherValue = `no-${unique}`;
	const secondParentText = `second-parent-${unique}`;
	const secondTriggerValue = `second-yes-${unique}`;
	const secondOtherValue = `second-no-${unique}`;

	await login(page, "admin@mondey.de", "admin");
	await expect(
		page.getByText("Wählen sie ein Kind zur Beobachtung aus"),
	).toBeVisible();

	if (isMobile) {
		await page.getByTestId("mobile-userland-navbar").click();
	}
	await page.getByRole("link", { name: "Administration" }).click();
	await page.locator('button:has-text("Fragen über Kind")').click();

	async function createParentQuestion(text: string, optionValues: string[]) {
		await page.locator('button:has-text("Hinzufügen")').click();
		await page.getByTestId("text-question-input-de").fill(text);
		await page.getByTestId("visibility-checkbox").setChecked(true);
		await page.selectOption('[data-testid="questionTypeSelect"]', {
			label: "Multiple Choice",
		});
		// Fill every language so options_json is populated for the locale used on
		// the child form.
		const options = optionValues.join(";");
		await page.getByPlaceholder("Option values").fill(options);
		const displayedOptions = page.getByPlaceholder("Displayed options");
		const numLanguages = await displayedOptions.count();
		for (let i = 0; i < numLanguages; i++) {
			await displayedOptions.nth(i).fill(options);
		}
		await page.locator('button:has-text("Änderungen speichern")').click();
		await expect(page.getByText(text)).toBeVisible();
	}

	// Create two parents with disjoint options so changing parents can also test
	// that trigger values from the previous parent are discarded.
	await createParentQuestion(parentText, [triggerValue, otherValue]);
	await createParentQuestion(secondParentText, [
		secondTriggerValue,
		secondOtherValue,
	]);

	// --- create the dependent question ---
	await page.locator('button:has-text("Hinzufügen")').click();
	await page.getByTestId("text-question-input-de").fill(dependentText);
	await page.getByTestId("visibility-checkbox").setChecked(true);
	await page.selectOption('[data-testid="questionTypeSelect"]', {
		label: "Text",
	});
	// make it depend on the parent question, shown only for the trigger value
	await page.selectOption('[data-testid="dependsOnSelect"]', {
		label: parentText,
	});
	await page.getByRole("checkbox", { name: triggerValue }).check();
	await page.selectOption('[data-testid="dependsOnSelect"]', {
		label: secondParentText,
	});
	await expect(
		page.getByRole("checkbox", { name: secondTriggerValue }),
	).not.toBeChecked();
	await page.selectOption('[data-testid="dependsOnSelect"]', {
		label: parentText,
	});
	await expect(
		page.getByRole("checkbox", { name: triggerValue }),
	).not.toBeChecked();
	await page.getByRole("checkbox", { name: triggerValue }).check();
	await page.locator('button:has-text("Änderungen speichern")').click();
	await expect(page.getByText(dependentText)).toBeVisible();

	// --- verify behaviour on the create-child form ---
	await page.goto("/userLand/children");
	await page.locator('h5:has-text("+ Neu")').click();

	// the parent question is always shown, the dependent one is hidden initially
	await expect(page.getByText(parentText, { exact: true })).toBeVisible();
	await expect(page.getByText(dependentText)).toHaveCount(0);

	const parentSelect = page
		.locator("select")
		.filter({ has: page.locator(`option[value="${triggerValue}"]`) });

	// answering the parent with the trigger value reveals the dependent question
	await parentSelect.selectOption({ label: triggerValue });
	await expect(page.getByText(dependentText)).toBeVisible();

	// Fill in the dependent answer. Other E2E tests may have added textareas to
	// this form already, so identify this one by its question name.
	const dependentTextarea = page.locator(
		`form textarea[for="${dependentText}"]`,
	);
	await dependentTextarea.fill("an answer that should be cleared");

	// switching the parent to a non-trigger value hides the dependent question
	await parentSelect.selectOption({ label: otherValue });
	await expect(page.getByText(dependentText)).toHaveCount(0);

	// switching back reveals it again, now with a cleared (empty) answer
	await parentSelect.selectOption({ label: triggerValue });
	await expect(page.getByText(dependentText)).toBeVisible();
	await expect(dependentTextarea).toHaveValue("");
});
