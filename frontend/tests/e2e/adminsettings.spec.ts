import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("admin settings document upload", async ({ page }) => {
	await login(page, "admin@mondey.de", "admin");

	// go to admin page
	await expect(page.locator('h5:has-text("+ Neu")')).toBeVisible();
	await page.getByText("Administration").click();
	await expect(page.getByText("Voraussichtliches Alter")).toBeVisible();

	// go to AdminDocuments tab
	await page.getByText("Admin Dokumente").click();
	await expect(page.getByText("Mondey-Publikationen")).toBeVisible();

	// Click add button to open upload modal
	await page.getByRole("button", { name: "Hinzufügen" }).click();
	await expect(page.getByText("Dokument hochladen")).toBeVisible();

	const testTitle = `Test Doc ${crypto.randomUUID().substring(0, 8)}`;
	await page.fill("#title", testTitle);
	await page.fill(
		"#description",
		"Test document description for automated testing",
	);
	// Upload fake PDF file
	const fileInput = page.locator('input[type="file"]');
	await fileInput.setInputFiles("tests/fixtures/test-document.pdf");

	// Submit
	await page.getByRole("button", { name: "Hochladen" }).click();

	// wait for modal to close and verify document appears in table
	await expect(page.getByText("Dokument hochladen")).toBeHidden();
	await expect(page.getByText(testTitle.substring(0, 10))).toBeVisible();

	// we dont' check it appears on the overall overview page because we'd have to deal with the hardcoded mondey.de bit
	// with an artifical, test-purpose made only query string or somethjing.
});
