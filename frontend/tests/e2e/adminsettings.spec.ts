import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("admin settings document upload", async ({ page }) => {
	await login(page, "admin@mondey.de", "admin");

	// go to admin page
	await expect(page.locator('h5:has-text("+ Neu")')).toBeVisible();
	await page.getByText("Administration").click();
	await expect(page.getByText("Voraussichtliches Alter")).toBeVisible();

	// go to AdminDocuments tab
	await page.getByText("Dokumente").click();
	await expect(page.getByText("Mondey-Publikationen")).toBeVisible();

	// Click add button to open upload modal
	await page.getByRole("button", { name: "Hinzufügen" }).click();
	await expect(page.getByText("Dokument hochladen")).toBeVisible();

	// Generate a unique name & description for this document
	const testTitle = `doc-${crypto.randomUUID()}`;
	const testDescription = `desc-${crypto.randomUUID()}`;
	await page.fill("#title", testTitle);
	await page.fill("#description", testDescription);

	// Upload minimal PDF file
	const pdfFileToUpload = {
		name: `${testTitle}.pdf`,
		mimeType: "application/pdf",
		buffer: Buffer.from(
			"%PDF-1.1\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Size 1/Root 1 0 R>>\nstartxref\n15\n%%EOF",
			"binary",
		),
	};
	const fileInput = page.locator('input[type="file"]');
	await fileInput.setInputFiles([pdfFileToUpload]);

	// Submit
	await page.getByRole("button", { name: "Hochladen" }).click();

	// wait for modal to close and verify document appears in table
	await expect(page.getByText("Dokument hochladen")).toBeHidden();
	await expect(page.getByText(testTitle)).toBeVisible();

	// check that the uploaded document appears on the downloads page
	await page.goto("/downloads", { waitUntil: "networkidle" });
	const card = page.getByTestId(testTitle);
	await expect(card).toBeVisible();
	await expect(card.getByText(testTitle)).toBeVisible();

	// check that we can download the document from the downloads page
	const downloadPromise = page.waitForEvent("download");
	await card.getByText("Herunterladen").click();
	const download = await downloadPromise;
	expect(download.suggestedFilename()).toEqual(`${testTitle}.pdf`);
});
