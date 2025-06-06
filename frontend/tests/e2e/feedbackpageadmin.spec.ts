/*

This page will use SQL provided stats data and we will check that the data we expect appears from there,
ratehr than use the UI to manually add the data etc.

 */

import { expect, test } from "@playwright/test";
import { DateTime } from "luxon";
import { login } from "./utils";

test("/userLand/children - The gallery of children includes feedback with the relevant milestone groups", async ({
	page,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await expect(
		page.getByText("Wählen sie ein Kind zur Beobachtung aus"),
	).toBeVisible();

	// Emma Johnson was born 3 months ago
	const birthDate = DateTime.now().minus({ months: 3 });
	await expect(
		page.getByText(`${birthDate.month}/${birthDate.year}`),
	).toBeVisible();

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

	await expect(
		page.getByText("Noch nicht genügend Daten für Feedback"),
	).toBeVisible();
});
