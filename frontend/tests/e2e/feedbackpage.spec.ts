/*

This page will use SQL provided stats data and we will check that the data we expect appears from there,
ratehr than use the UI to manually add the data etc.

 */

import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/admin - Questions on Children : New question can be added, and appears on the create child form", async ({
	page,
}) => {
	await login(page, "admin@mondey.de", "admin");

	await page.locator('h5:has-text("Emma Johnson")').click();
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

	// This is our circular checkmark.
	// todo: There could be checkmarks for other milestone groups. Solution:
	// I think maybe alter the code to have a testdataID for milestone feedback (e.g. Grun, Fragenzeichern, Verzögerung)
	// The code right now displays these as elements so it might mean rewriting though but this is important.

	await expect(
		page.locator("svg.shrink-0.w-8.h-8.text-feedback-0").first(),
	).toBeAttached();
});
