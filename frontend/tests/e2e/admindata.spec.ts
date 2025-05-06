import { expect, test } from "@playwright/test";
import { login } from "./utils";

test("admin Data tab", async ({ page }) => {
	await login(page, "admin@mondey.de", "admin");

	// go to admin page
	await expect(page.locator('h5:has-text("+ Neu")')).toBeVisible();
	await page.getByText("Administration").click();
	await expect(page.getByText("Voraussichtliches Alter")).toBeVisible();

	// go to Daten tab
	await page.getByRole("tab", { name: "Daten" }).click();
	const onlySuspiciousCheckbox = page.getByText("nur verdächtige anzeigen");
	await expect(onlySuspiciousCheckbox).toBeVisible();
	// initially only 1004 is visible as it is the only one marked as suspicious
	await expect(page.getByText("1003")).not.toBeVisible();
	await expect(page.getByText("1004")).toBeVisible();
	await expect(page.getByText("1005")).not.toBeVisible();
	// show all answer sessions
	await onlySuspiciousCheckbox.click();
	await expect(page.getByText("1003")).toBeVisible();
	await expect(page.getByText("1004")).toBeVisible();
	await expect(page.getByText("1005")).toBeVisible();

	// open & close analysis modal
	await page.getByTestId("analyze-1011").click();
	await page.getByText("rms").isVisible();
	await page.getByTestId("cancelButton").click();
	await expect(page.getByTestId("cancelButton")).toBeHidden();

	// do a partial statistics update
	await page.getByTestId("incrementalStatsUpdate").click();
	await expect(page.getByText("nur verdächtige anzeigen")).toBeVisible();
	await page.getByTestId("closeUpdateStatsModal").isEnabled();
	await page.getByTestId("closeUpdateStatsModal").click();
	await expect(page.getByTestId("closeUpdateStatsModal")).toBeHidden();

	// do a full statistics update
	await page.getByTestId("fullStatsUpdate").click();
	await expect(page.getByText("nur verdächtige anzeigen")).toBeVisible();
	await page.getByTestId("closeUpdateStatsModal").isEnabled();
	await page.getByTestId("closeUpdateStatsModal").click();
	await expect(page.getByTestId("closeUpdateStatsModal")).toBeHidden();
});
