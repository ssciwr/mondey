/*

This page will use SQL provided stats data and we will check that the data we expect appears from there,
ratehr than use the UI to manually add the data etc.

 */

import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("/userLand/children - The gallery of children includes feedback with the relevant milestone groups", async ({
	page,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await expect(
		page.getByText("Wählen sie ein Kind zur Beobachtung aus"),
	).toBeVisible();

	await page.locator('h5:has-text("Emma Johnson")').click();
	await expect(page.getByText("2025", { exact: false }).first()).toBeVisible(); //  we don't test the month because it's variable in a
	// complicated way in the SQL which inserts the children (importMIlestoneAnswer.sql) to keep them around 3 months
	// old at time of test.

	await page.locator('button:has-text("Feedback zur Entwicklung")').click();

	await expect(
		page.locator('span:has-text("Textlesen")').first(),
	).toBeAttached();
	await expect(
		page.locator('span:has-text("Tanzfähigkeiten")').first(),
	).toBeAttached();

	await expect(
		page.locator('span:has-text("Tanzfähigkeiten")').last(),
	).toBeAttached();

	await expect(
		page.locator("svg.shrink-0.w-8.h-8.text-feedback-0").first(),
	).toBeAttached();
});
