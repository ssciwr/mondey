import * as fs from "node:fs";
import { type Locator, type Page, expect } from "@playwright/test";
import { translationIds } from "#lib/translations.ts";
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

// Mock the progress and final data returned by the /research/data route.
async function mock_research_data_route(
	page: Page,
	n_answer_sessions: number,
	n_milestones: number,
	transform = (row: Record<string, string | number | null>) => row,
) {
	await page.route("**/research/data/**", async (route) => {
		const data = make_research_data(n_answer_sessions, n_milestones).map(
			transform,
		);
		await route.fulfill({
			contentType: "application/jsonl",
			body: `${JSON.stringify({ type: "progress", stage: "assembling" })}\n${JSON.stringify({ type: "data", data })}\n`,
		});
	});
}

// Mock the /research/names route
async function mock_research_names_route(
	page: Page,
	n_milestones: number,
	child_question: Record<number, string> = {
		"1": "Number of Siblings",
		"2": "Early birth",
	},
) {
	await page.route("**/research/names/**", async (route) => {
		const json: Record<string, Record<number, string>> = {
			milestone: {},
			user_question: { "1": "Parent income" },
			child_question,
		};
		for (let milestone_id = 1; milestone_id <= n_milestones; ++milestone_id) {
			json.milestone[`${milestone_id}`] =
				`MS${n_milestones - milestone_id + 1}`;
		}
		json.milestone_label = Object.fromEntries(
			Object.entries(json.milestone).map(([id, name]) => [
				id,
				`${name} :: Group ${name.slice(2)} :: Milestone ${name.slice(2)}`,
			]),
		);
		await route.fulfill({ json });
	});
}

// Loading takes longer than the default expect timeout when many tests run in parallel.
async function expect_research_data_loaded(page: Page) {
	await expect(page.getByTestId("downloadAllResearchData")).toBeEnabled({
		timeout: 20000,
	});
}

async function clickDownloadCSVButtonAndGetFilename(
	page: Page,
	allData = false,
): Promise<string> {
	const downloadPromise = page.waitForEvent("download");
	await page
		.getByTestId(allData ? "downloadAllResearchData" : "researchDownloadCSV")
		.click();
	const download = await downloadPromise;
	return download.suggestedFilename();
}

// selectOption doesn't work with the flowbite-svelte multiselect component,
// so this class abstracts the workarounds found for interacting with it.
class Multiselect {
	private page: Page;
	private readonly placeholder: string;
	private currentText: string;
	constructor(page: Page, placeholder: string) {
		this.page = page;
		this.placeholder = placeholder;
		this.currentText = placeholder;
	}
	private locater() {
		// select which listbox we want based on the text currently displayed in it
		return this.page.getByRole("listbox").filter({ hasText: this.currentText });
	}
	private async toggleDropdown() {
		// click on up/down svg arrow to open/close drop-down
		// locate it as the last svg element of the listbox
		await this.locater().locator("svg").locator("nth=-1").click();
	}
	async clear() {
		await this.locater().getByRole("button", { name: "Close" }).click();
		this.currentText = this.placeholder;
	}
	async select(text: string) {
		// open drop-down menu
		await this.toggleDropdown();
		// click on element with text in drop-down
		// (the hidden select element inside the listbox also contains options with the same text)
		await this.locater().getByRole("presentation").getByText(text).click();
		this.currentText = text;
		// open drop-down menu
		await this.toggleDropdown();
	}
}

test("Research page: valid data", async ({ page }) => {
	await mock_research_data_route(page, 20, 5);
	await mock_research_names_route(page, 5);
	await page.goto("/userLand/research", { waitUntil: "networkidle" });

	await expect(
		page.getByTestId("selectMilestone").locator("option"),
	).toHaveText(
		Array.from(
			{ length: 5 },
			(_, index) =>
				`MS${index + 1} :: Group ${index + 1} :: Milestone ${index + 1}`,
		),
	);

	// select first milestone
	const selectMilestone = new Multiselect(
		page,
		translationIds.researcher.milestones,
	);
	await selectMilestone.select("MS1 :: Group 1 :: Milestone 1");
	// plot and table of data for first milestone should be displayed
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toContainText("punktzahl");
	const plot_title = page.getByTestId("researchPlotTitle");
	await expect(plot_title).toContainText("MS1");
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
	expect(downloadFilename).toContain("MS1");

	// select two more milestones
	await selectMilestone.select("MS2");
	await selectMilestone.select("MS3");
	await expect(plot_title).toContainText("MS1");
	await expect(plot_title).toContainText("MS2");
	await expect(plot_title).toContainText("MS3");
	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("MS1");
	expect(downloadFilename).toContain("MS2");
	expect(downloadFilename).toContain("MS3");

	// group by parent income
	await expect(table).not.toContainText("Parent income");
	const selectGroupby = new Multiselect(
		page,
		translationIds.researcher.groupbyOptional,
	);
	await selectGroupby.select("Parent income");
	await expect(table).toContainText("Parent income");
	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("MS1");
	expect(downloadFilename).toContain("MS2");
	expect(downloadFilename).toContain("MS3");
	expect(downloadFilename).toContain("Parent income");

	// also group by number of siblings
	await expect(table).not.toContainText("Number of Siblings");
	await selectGroupby.select("Number of Siblings");
	await expect(table).toContainText("Parent income");
	await expect(table).toContainText("Number of Siblings");
	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("MS1");
	expect(downloadFilename).toContain("MS2");
	expect(downloadFilename).toContain("MS3");
	expect(downloadFilename).toContain("Parent income");
	expect(downloadFilename).toContain("Number of Siblings");

	// clear groupby selection
	await selectGroupby.clear();
	await expect(table).not.toContainText("Parent income");
	await expect(table).not.toContainText("Number of Siblings");
	// download CSV
	downloadFilename = await clickDownloadCSVButtonAndGetFilename(page);
	expect(downloadFilename).toContain("mondey");
	expect(downloadFilename).toContain("MS1");
	expect(downloadFilename).toContain("MS2");
	expect(downloadFilename).toContain("MS3");
	expect(downloadFilename).not.toContain("Parent income");
	expect(downloadFilename).not.toContain("Number of Siblings");

	// clear milestone selection
	await selectMilestone.clear();
	// no plot or table are displayed if there is no data
	await expect(plot).toHaveCount(0);
	await expect(table).toHaveCount(0);
});

test("Research page: no data", async ({ page }) => {
	await mock_research_data_route(page, 0, 0);
	await mock_research_names_route(page, 0);
	const dataResponse = page.waitForResponse("**/research/data/**");
	await page.goto("/userLand/research");
	await dataResponse;
	await expect(page.getByText(translationIds.researcher.noData)).toBeVisible();
	await expect(page.getByTestId("researchLoadProgress")).toHaveCount(0);

	// no plot or table are displayed if there is no data
	const plot = page.getByTestId("researchPlotLines");
	await expect(plot).toHaveCount(0);
	const table = page.getByTestId("researchTable");
	await expect(table).toHaveCount(0);
});

test("Research page: grouping by an unanswered question shows no data", async ({
	page,
}) => {
	await mock_research_data_route(page, 20, 5, (row) => ({
		...row,
		child_question_2: null,
	}));
	await mock_research_names_route(page, 5);
	await page.goto("/userLand/research");
	await expect_research_data_loaded(page);
	await new Multiselect(page, translationIds.researcher.milestones).select(
		"MS1 :: Group 1 :: Milestone 1",
	);
	await expect(page.getByTestId("researchTable")).toBeVisible();
	await new Multiselect(page, translationIds.researcher.groupbyOptional).select(
		"Early birth",
	);
	await expect(page.getByTestId("researchTable")).toHaveCount(0);
	await expect(page.getByTestId("researchPlotLines")).toHaveCount(0);
	await expect(page.getByRole("alert")).toHaveCount(0);
	await expect(page.getByTestId("downloadAllResearchData")).toBeEnabled();
});

test("Research page: a failed download keeps the loaded data usable", async ({
	page,
}) => {
	await mock_research_data_route(page, 20, 5);
	// A question without a name makes the worker fail to build the CSV header.
	await mock_research_names_route(page, 5, { "1": "Number of Siblings" });
	await page.goto("/userLand/research");
	const downloadAll = page.getByTestId("downloadAllResearchData");
	await downloadAll.click();
	await expect(page.getByTestId("researchProcessingError")).toBeVisible();
	await expect(page.getByTestId("researchLoadError")).toHaveCount(0);
	await expect(downloadAll).toBeEnabled();
	await new Multiselect(page, translationIds.researcher.milestones).select(
		"MS1 :: Group 1 :: Milestone 1",
	);
	await expect(page.getByTestId("researchTable")).toBeVisible();
	await expect(page.getByTestId("researchProcessingError")).toHaveCount(0);
});

test("Research page: progress stays visible until browser preparation finishes", async ({
	page,
}) => {
	await mock_research_data_route(page, 20, 5);
	let releaseNames!: () => void;
	const namesGate = new Promise<void>((resolve) => {
		releaseNames = resolve;
	});
	await mock_research_names_route(page, 5);
	await page.route("**/research/names/**", async (route) => {
		await namesGate;
		await route.fallback();
	});
	const namesRequest = page.waitForRequest("**/research/names/**");
	await page.goto("/userLand/research");
	await namesRequest;
	const loading = page.getByTestId("researchLoadProgress");
	const modal = page.getByRole("dialog", {
		name: translationIds.researcher.loadingResearchData,
	});
	await expect(modal).toBeVisible();
	await expect(modal.getByRole("button")).toHaveText(
		translationIds.admin.cancel,
	);
	await expect(loading).toContainText(translationIds.researcher.loadingNames);
	await expect(loading.getByRole("progressbar")).toHaveAttribute("value", "9");
	await expect(page.getByTestId("downloadAllResearchData")).toBeDisabled();
	await page.keyboard.press("Escape");
	await expect(modal).toBeVisible();
	await page.mouse.click(5, 5);
	await expect(modal).toBeVisible();
	releaseNames();
	await expect(loading).toHaveCount(0);
	await expect(modal).toHaveCount(0);
	await expect_research_data_loaded(page);
});

test("Research page: loading can be cancelled and restarted", async ({
	page,
}) => {
	await mock_research_data_route(page, 20, 5);
	await mock_research_names_route(page, 5);
	const stall = () => {
		// Never respond, so loading cannot finish before it is cancelled.
	};
	await page.route("**/research/names/**", stall);
	const namesRequest = page.waitForRequest("**/research/names/**");
	await page.goto("/userLand/research");
	await namesRequest;
	const modal = page.getByRole("dialog", {
		name: translationIds.researcher.loadingResearchData,
	});
	await modal
		.getByRole("button", { name: translationIds.admin.cancel })
		.click();
	await expect(modal).toHaveCount(0);
	await expect(page.getByTestId("researchLoadError")).toContainText(
		translationIds.researcher.loadCancelled,
	);
	await expect(page.getByTestId("downloadAllResearchData")).toBeDisabled();
	await page.unroute("**/research/names/**", stall);
	await page
		.getByRole("button", { name: translationIds.researcher.retry })
		.click();
	await expect(page.getByTestId("researchLoadError")).toHaveCount(0);
	await expect_research_data_loaded(page);
});

test("Research page: a failed load can be retried", async ({ page }) => {
	await mock_research_data_route(page, 20, 5);
	await mock_research_names_route(page, 5);
	await page.route(
		"**/research/data/**",
		async (route) => {
			await route.fulfill({
				contentType: "application/jsonl",
				body: '{"type":"error"}\n',
			});
		},
		{ times: 1 },
	);
	const failedResponse = page.waitForResponse("**/research/data/**");
	await page.goto("/userLand/research");
	await failedResponse;
	await expect(page.getByTestId("researchLoadError")).toBeVisible();
	await expect(page.getByRole("dialog")).toHaveCount(0);
	await expect(page.getByTestId("downloadAllResearchData")).toBeDisabled();
	const retryResponse = page.waitForResponse("**/research/data/**");
	await page
		.getByRole("button", { name: translationIds.researcher.retry })
		.click();
	await retryResponse;
	await expect(page.getByTestId("researchLoadError")).toHaveCount(0);
	await expect_research_data_loaded(page);
});

test("Research page: Download all CSV contains expected data", async ({
	page,
}) => {
	await mock_research_data_route(page, 20, 5);
	await mock_research_names_route(page, 5);
	await page.goto("/userLand/research", { waitUntil: "networkidle" });
	const downloadFilename = await clickDownloadCSVButtonAndGetFilename(
		page,
		true,
	);
	expect(downloadFilename).toContain("mondey_all_");
});
