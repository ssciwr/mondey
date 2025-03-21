import { type Page, expect, test } from "@playwright/test";

// Return a random integer from the inclusive range [min, max]
function sample(min: number, max: number): number {
	return min + Math.floor(Math.random() * (max - min + 1));
}

// Generate some data to be displayed by the research page
function make_research_data(n_answer_sessions = 20, n_milestones = 5) {
	const data: Array<Record<string, string | number>> = [];
	let answer_session_id = 1;
	for (let i = 0; i < n_answer_sessions; ++i) {
		for (let milestone_id = 1; milestone_id <= n_milestones; ++milestone_id) {
			data.push({
				milestone_group_id: 1,
				milestone_id: milestone_id,
				answer: sample(1, 4),
				child_age: sample(1, 72),
				answer_session_id: answer_session_id,
				number_of_siblings: sample(0, 5),
				"early birth": ["yes", "no"][sample(0, 1)],
			});
			++answer_session_id;
		}
	}
	return data;
}

// Mock the /research/data route
async function mock_research_data_route(page: Page) {
	await page.route("**/research/data/", async (route) => {
		const json = make_research_data();
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

test("Research page: valid data", async ({ page }) => {
	await mock_user_route(page);
	await mock_research_data_route(page);
	await page.goto("/userLand/research");

	// plot and table of data should be displayed
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toContainText("punktzahl");
	const plot_title = page.getByTestId("researchPlotTitle");
	await expect(plot_title).toContainText("Meilenstein 1");
	const table = page.getByTestId("researchTable");
	await expect(table).toContainText("1");
	await expect(table).toContainText("milestone_id");
	await expect(table).toContainText("child_age");
	await expect(table).toContainText("answer_mean");
	await expect(table).toContainText("answer_std");
	await expect(table).toContainText("answer_count");
	await expect(table).not.toContainText("number_of_siblings");
	await expect(table).not.toContainText("early birth");

	// click download as CSV button
	const downloadPromise = page.waitForEvent("download");
	page.getByTestId("researchDownloadCSV").click();
	const download = await downloadPromise;
	expect(download.suggestedFilename()).toContain("mondey");

	// select another milestone
	const selectMilestone = page.getByTestId("selectMilestone");
	await selectMilestone.selectOption("3");
	await expect(plot_title).toContainText("Meilenstein 3");
});

test("Research page: no data", async ({ page }) => {
	await mock_user_route(page);
	await page.goto("/research");

	// no plot or table are displayed if there is no data
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toHaveCount(0);
	const table = page.getByTestId("researchTable");
	await expect(table).toHaveCount(0);
});
