import { translationIds } from "$lib/translations";
import { type Locator, type Page, expect } from "@playwright/test";
import { test } from "./test";

// Return a random integer from the inclusive range [min, max]
function sample(min: number, max: number): number {
	return min + Math.floor(Math.random() * (max - min + 1));
}

// Generate some data to be displayed by the research page
function make_research_data(n_answer_sessions = 20, n_milestones = 5) {
	const data: Array<Record<string, string | number>> = [];
	let answer_session_id = 1;
	for (let i = 0; i < n_answer_sessions; ++i) {
		const row: Record<string, string | number> = {
			child_age: sample(1, 72),
			answer_session_id: answer_session_id,
			child_question_1: sample(0, 5),
			child_question_2: ["yes", "no"][sample(0, 1)],
			user_question_1: ["low", "middle", "high"][sample(0, 2)],
		};
		for (let milestone_id = 1; milestone_id <= n_milestones; ++milestone_id) {
			row[`milestone_id_${milestone_id}`] = sample(1, 4);
		}
		data.push(row);
		++answer_session_id;
	}
	return data;
}

// Mock the /research/data route
async function mock_research_data_route(
	page: Page,
	n_answer_sessions: number,
	n_milestones: number,
) {
	await page.route("**/research/data/", async (route) => {
		const json = make_research_data(n_answer_sessions, n_milestones);
		await route.fulfill({ json });
	});
}

// Mock the /research/names route
async function mock_research_names_route(page: Page, n_milestones: number) {
	await page.route("**/research/names/", async (route) => {
		const json: Record<string, Record<number, string>> = {
			milestone: {},
			user_question: { "1": "Parent income" },
			child_question: { "1": "Number of Siblings", "2": "Early birth" },
		};
		for (let milestone_id = 1; milestone_id <= n_milestones; ++milestone_id) {
			json.milestone[`${milestone_id}`] = `Milestone ${milestone_id}`;
		}
		await route.fulfill({ json });
	});
}

async function clickDownloadCSVButtonAndGetFilename(
	page: Page,
): Promise<string> {
	const downloadPromise = page.waitForEvent("download");
	await page.getByTestId("researchDownloadCSV").click();
	const download = await downloadPromise;
	return download.suggestedFilename();
}

// selectOption doesn't work with the flowbite-svelte multiselect component,
// so this class abstracts the workarounds found for interacting with it.
class GroupbyMultiselect {
	private locator: Locator;
	constructor(page: Page) {
		this.locator = page.getByRole("listbox");
	}
	async clear() {
		await this.locator.getByRole("button", { name: "Close" }).click();
	}
	async select(text: string) {
		await this.locator.click();
		await this.locator.getByText(text).click();
	}
}

test("Research page: valid data", async ({ page }) => {
	await mock_research_data_route(page, 20, 5);
	await mock_research_names_route(page, 5);
	await page.goto("/userLand/research");

	// plot and table of data for first milestone should be displayed
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toContainText("punktzahl");
	const plot_title = page.getByTestId("researchPlotTitle");
	await expect(plot_title).toContainText("Milestone 1");
	const table = page.getByTestId("researchTable");
	await expect(table).toContainText("1");
	await expect(table).toContainText("child_age");
	await expect(table).toContainText("answer_mean");
	await expect(table).toContainText("answer_std");
	await expect(table).toContainText("answer_count");
	await expect(table).not.toContainText("Parent income");

	// download CSV
	let downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("milestone_id_1");

	// select another milestone
	const selectMilestone = page.getByTestId("selectMilestone");
	await selectMilestone.selectOption("Milestone 3");
	await expect(plot_title).toContainText("Milestone 3");

	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("milestone_id_3");

	// group by parent income
	await expect(table).not.toContainText("Parent income");
	const selectGroupby = new GroupbyMultiselect(page);
	await selectGroupby.select("Parent income");
	await expect(table).toContainText("Parent income");

	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("milestone_id_3");
	expect(downloadFilename).toContain("user_question_1");

	// also group by number of siblings
	await expect(table).not.toContainText("Number of Siblings");
	await selectGroupby.select("Number of Siblings");
	await expect(table).toContainText("Parent income");
	await expect(table).toContainText("Number of Siblings");

	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("milestone_id_3");
	expect(downloadFilename).toContain("user_question_1");
	expect(downloadFilename).toContain("child_question_1");

	// clear groupby selection
	await selectGroupby.clear();
	await expect(table).not.toContainText("Parent income");
	await expect(table).not.toContainText("Number of Siblings");

	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("milestone_id_3");
	expect(downloadFilename).not.toContain("question");
});

test("Research page: no data", async ({ page }) => {
	await mock_research_data_route(page, 0, 0);
	await page.goto("/userLand/research");

	// no plot or table are displayed if there is no data
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toHaveCount(0);
	const table = page.getByTestId("researchTable");
	await expect(table).toHaveCount(0);
});
