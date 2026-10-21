import { expect, test } from "@playwright/test";
import { DateTime } from "luxon";
import { login } from "./utils";

test("double clicking a milestone answer only answers the current milestone", async ({
	page,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await expect(page.locator('h5:has-text("+ Neu")')).toBeVisible();

	// create a child owned by this test, so browser projects can run concurrently
	// (with an age that none of the e2e test data children have, so other tests can find those by birth date)
	const childName = `double-click-${crypto.randomUUID().slice(0, 8)}`;
	const birthDate = DateTime.now().minus({ months: 4 });
	const createResponse = await page.request.post("/api/users/children/", {
		data: {
			name: childName,
			birth_year: birthDate.year,
			birth_month: birthDate.month,
		},
	});
	expect(createResponse.ok()).toBeTruthy();
	const child = (await createResponse.json()) as { id: number };

	// open the first milestone of a milestone group
	await page.reload();
	await page.locator(`h5:has-text("${childName}")`).click();
	await page.locator('button:has-text("Weiter zu Meilensteinen")').click();
	await page.getByText("Textlesen").first().click();
	await page.locator(".main-content h5").first().click();
	const position = page.locator("nav ol li").last();
	await expect(position).toHaveText(/^\s*1\/\d+$/);

	// slow down saving the answer, so that the second click happens while the first answer is being saved
	let answerRequests = 0;
	await page.route("**/api/users/milestone-answers/**", async (route) => {
		answerRequests += 1;
		await new Promise((resolve) => setTimeout(resolve, 500));
		await route.continue();
	});

	await page
		.getByRole("button", { name: /In Ansätzen/ })
		.first()
		.dblclick();

	// the answer is saved once, and the next milestone is shown (rather than skipping one)
	await expect(position).toHaveText(/^\s*2\/\d+$/);
	await page.waitForTimeout(1000);
	await expect(position).toHaveText(/^\s*2\/\d+$/);
	expect(answerRequests).toBe(1);

	await page.unrouteAll();
	const deleteResponse = await page.request.delete(
		`/api/users/children/${child.id}`,
	);
	expect(deleteResponse.ok()).toBeTruthy();
});
