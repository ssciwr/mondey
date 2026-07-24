import { translationIds } from "$lib/translations";
import { expect, test } from "@playwright/test";

test("admin can make a user a researcher and assign a research code", async ({
	page,
}) => {
	const admin = {
		id: 1,
		email: "admin@example.com",
		is_active: true,
		is_superuser: true,
		is_verified: true,
		is_researcher: false,
		full_data_access: false,
		research_group_id: 0,
	};
	let ordinaryUser = {
		id: 4,
		email: "ordinary@example.com",
		is_active: true,
		is_superuser: false,
		is_verified: true,
		is_researcher: false,
		full_data_access: false,
		research_group_id: 0,
	};
	let researcherUpdateReceived = false;
	let researchCodeRequestReceived = false;

	await page.route("**/languages/", async (route) => {
		await route.fulfill({ json: ["de"] });
	});
	await page.route("**/static/i18n/de.json", async (route) => {
		await route.fulfill({ json: translationIds });
	});
	await page.route("**/users/me", async (route) => {
		await route.fulfill({ json: admin });
	});
	await page.route("**/admin/milestone-groups/", async (route) => {
		await route.fulfill({ json: [] });
	});
	await page.route("**/admin/users/", async (route) => {
		await route.fulfill({ json: [admin, ordinaryUser] });
	});
	await page.route("**/users/4", async (route) => {
		const update = await route.request().postDataJSON();
		expect(update).toMatchObject({
			is_researcher: true,
			full_data_access: false,
		});
		researcherUpdateReceived = true;
		ordinaryUser = { ...ordinaryUser, ...update };
		await route.fulfill({ json: ordinaryUser });
	});
	await page.route("**/admin/research-groups/4", async (route) => {
		researchCodeRequestReceived = true;
		ordinaryUser = {
			...ordinaryUser,
			is_researcher: true,
			research_group_id: 123451,
		};
		await route.fulfill({ json: { id: ordinaryUser.research_group_id } });
	});

	await page.goto("/userLand/admin");
	await page.getByRole("tab", { name: translationIds.admin.users }).click();

	const userRow = page.getByRole("row").filter({ hasText: ordinaryUser.email });
	await expect(userRow).toBeVisible();
	const tableHead = page.locator("thead");
	for (const heading of [
		translationIds.admin.userEmail,
		translationIds.admin.userActive,
		translationIds.admin.userVerified,
		translationIds.admin.userResearcher,
		translationIds.admin.userFullDataAccess,
		translationIds.admin.userResearchCode,
		translationIds.admin.userAdmin,
	]) {
		await expect(tableHead).toContainText(heading);
	}

	const researcherCheckbox = userRow.getByRole("checkbox").nth(2);
	await expect(researcherCheckbox).not.toBeChecked();
	await researcherCheckbox.check();
	await userRow
		.getByRole("button", { name: translationIds.admin.saveChanges })
		.click();

	await expect.poll(() => researcherUpdateReceived).toBe(true);
	await userRow
		.getByRole("button", { name: translationIds.admin.addResearchCode })
		.click();

	await expect.poll(() => researchCodeRequestReceived).toBe(true);
	await expect(userRow).toContainText("123451");
});
