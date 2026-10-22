import { expect, test } from "@playwright/test";
import { translationIds } from "#lib/translations.ts";

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

test("admin can search, filter and page through users", async ({ page }) => {
	const makeUser = (id: number, email: string) => ({
		id,
		email,
		is_active: true,
		is_superuser: false,
		is_verified: true,
		is_researcher: false,
		full_data_access: false,
		research_group_id: 0,
	});
	const admin = { ...makeUser(1, "admin@example.com"), is_superuser: true };
	const researcher = {
		...makeUser(2, "researcher@example.com"),
		is_researcher: true,
		research_group_id: 123451,
	};
	const users = [admin, researcher];
	for (let i = 0; i < 60; i++) {
		users.push(makeUser(100 + i, `user${i}@example.com`));
		users.push(makeUser(200 + i, `${i}tester@testaccount.com`));
	}
	for (let i = 0; i < 30; i++) {
		users.push(makeUser(300 + i, `parent_of_${i}@artificialimporteddata.csv`));
	}

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
	let respondWithUsers = () => {};
	const usersRequested = new Promise<void>((resolve) => {
		respondWithUsers = resolve;
	});
	await page.route("**/admin/users/", async (route) => {
		await usersRequested;
		await route.fulfill({ json: users });
	});

	await page.goto("/userLand/admin");
	await page.getByRole("tab", { name: translationIds.admin.users }).click();

	// a spinner is shown until the users have loaded
	const spinner = page.getByTestId("usersLoading");
	await expect(spinner).toBeVisible();
	respondWithUsers();
	await expect(spinner).toBeHidden();

	const bodyRows = page.locator("tbody tr");
	const count = (n: number) => page.getByText(`${n} / ${users.length}`);
	const filters = page
		.locator("label")
		.filter({ has: page.getByRole("checkbox") });
	const filter = (label: string) => filters.filter({ hasText: label });

	// test and imported users are hidden by default, and only the first page of users is shown
	await expect(count(62)).toBeVisible();
	await expect(bodyRows).toHaveCount(50);
	await expect(page.locator("tbody")).not.toContainText("tester@");
	await expect(page.locator("tbody")).not.toContainText(
		"artificialimporteddata",
	);
	await page.getByRole("button", { name: "2", exact: true }).click();
	await expect(bodyRows).toHaveCount(12);

	// searching by email goes back to the first page
	const search = page.getByPlaceholder(
		translationIds.admin.userSearchPlaceholder,
	);
	await search.fill("USER1");
	await expect(bodyRows).toHaveCount(11);
	await search.fill("researcher@");
	await expect(bodyRows).toHaveCount(1);
	await expect(bodyRows).toContainText(researcher.email);
	await search.fill("");

	// account type checkboxes show users with any of the checked types
	await filter(translationIds.admin.userTestAccounts).click();
	await expect(count(122)).toBeVisible();
	await filter(translationIds.admin.userImportedAccounts).click();
	await expect(count(users.length)).toBeVisible();
	await filter(translationIds.admin.userNormalAccounts).click();
	await expect(count(90)).toBeVisible();
	await search.fill("59tester");
	await expect(bodyRows).toHaveCount(1);
	await search.fill("parent_of_29@");
	await expect(bodyRows).toHaveCount(1);
	await search.fill("");
	await filter(translationIds.admin.userTestAccounts).click();
	await expect(count(30)).toBeVisible();
	await filter(translationIds.admin.userImportedAccounts).click();
	await expect(count(0)).toBeVisible();
	await filter(translationIds.admin.userNormalAccounts).click();
	await expect(count(62)).toBeVisible();

	// role dropdown only shows users with the selected role
	const roleSelect = page.getByTestId("userRoleSelect");
	await roleSelect.selectOption("admin");
	await expect(bodyRows).toHaveCount(1);
	await expect(bodyRows).toContainText(admin.email);
	await roleSelect.selectOption("researcher");
	await expect(bodyRows).toHaveCount(1);
	await expect(bodyRows).toContainText(researcher.email);
	await filter(translationIds.admin.userNormalAccounts).click();
	await filter(translationIds.admin.userTestAccounts).click();
	await expect(count(0)).toBeVisible();
	await roleSelect.selectOption("all");
	await expect(count(60)).toBeVisible();
});
