import { translationIds } from "$lib/translations";
import type { Page } from "@playwright/test";
import { test as base } from "@playwright/test";

// Mock the languages routes to only include de, using the built-in frontend translations
async function mock_languages_routes(page: Page) {
	await page.route("**/languages/", async (route) => {
		const json = ["de"];
		await route.fulfill({ json });
	});
	await page.route("**/static/i18n/de.json", async (route) => {
		const json = translationIds;
		await route.fulfill({ json });
	});
}

// Mock the /users/me route with a valid User
async function mock_user_route(page: Page) {
	await page.route("**/users/me", async (route) => {
		const json = {
			id: 1,
			email: "researcher@mondey.de",
			is_active: true,
			is_superuser: false,
			is_verified: true,
			is_researcher: true,
			full_data_access: true,
			research_group_id: 703207,
		};
		await route.fulfill({ json });
	});
}

// Modify page fixture to include our mocks
export const test = base.extend({
	page: async ({ page }, use) => {
		await mock_languages_routes(page);
		await mock_user_route(page);
		await use(page);
	},
});
