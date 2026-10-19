import {
	cleanup,
	fireEvent,
	render,
	screen,
	waitFor,
} from "@testing-library/svelte";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.hoisted(() => {
	window.matchMedia = vi.fn().mockReturnValue({
		addEventListener: vi.fn(),
		matches: false,
		removeEventListener: vi.fn(),
	});
});

const mocks = vi.hoisted(() => ({
	getAdminSettings: vi.fn(),
	getCompletedMilestoneAnswerSessions: vi.fn(),
	getDetailedFeedbackForAnswersession: vi.fn(),
	getMilestonegroupsForSession: vi.fn(),
	getSummaryFeedbackForAnswersession: vi.fn(),
}));

vi.mock("$lib/client", () => mocks);
vi.mock("$app/navigation", () => ({ goto: vi.fn() }));
vi.mock("$lib/stores/childrenStore.svelte", () => ({
	currentChild: {
		id: 1,
		name: "Emma",
		month: 1,
		year: 2025,
		load_data: vi.fn(),
	},
}));
vi.mock("$lib/stores/userStore.svelte", () => ({
	user: { id: 1, data: { id: 1 } },
}));

import { alertStore } from "$lib/stores/alertStore.svelte";
import { translationIds as tr } from "$lib/translations";
import FeedbackPage from "./+page.svelte";

const sessions = {
	1: { id: 1, created_at: new Date().toISOString() },
};

describe("printing feedback reports", () => {
	const printWindow = {
		document: { write: vi.fn(), close: vi.fn() },
		print: vi.fn(),
		close: vi.fn(),
	};

	beforeEach(() => {
		vi.resetAllMocks();
		alertStore.hideAlert();
		vi.spyOn(window, "open").mockReturnValue(printWindow as unknown as Window);
		mocks.getAdminSettings.mockResolvedValue({
			data: {
				hide_milestone_feedback: false,
				hide_milestone_group_feedback: false,
				hide_all_feedback: false,
			},
		});
		mocks.getCompletedMilestoneAnswerSessions.mockResolvedValue({
			data: sessions,
		});
		mocks.getMilestonegroupsForSession.mockResolvedValue({
			data: {
				10: {
					id: 10,
					text: { de: { title: "Movement" } },
					milestones: [
						{ id: 100, text: { de: { title: "Walking" } } },
						{ id: 101, text: { de: { title: "Running" } } },
					],
				},
			},
		});
		mocks.getSummaryFeedbackForAnswersession.mockResolvedValue({
			data: { 10: 0 },
		});
		mocks.getDetailedFeedbackForAnswersession.mockResolvedValue({ data: {} });
	});

	afterEach(() => {
		cleanup();
		vi.restoreAllMocks();
	});

	async function printReport() {
		render(FeedbackPage);
		await fireEvent.click(
			await screen.findByRole("button", { name: tr.milestone.printReport }),
		);
		await waitFor(() => expect(printWindow.print).toHaveBeenCalledOnce());
		return printWindow.document.write.mock.calls[0][0] as string;
	}

	it("hides the print button when all feedback is disabled", async () => {
		mocks.getAdminSettings.mockResolvedValue({
			data: { hide_all_feedback: true },
		});
		mocks.getSummaryFeedbackForAnswersession.mockResolvedValue({ data: {} });
		render(FeedbackPage);
		await screen.findByRole("heading", { name: tr.milestone.feedbackTitle });
		expect(
			screen.queryByRole("button", { name: tr.milestone.printReport }),
		).toBeNull();
	});

	it("hides the print button when there are no completed observations", async () => {
		mocks.getCompletedMilestoneAnswerSessions.mockResolvedValue({ data: {} });
		render(FeedbackPage);
		await screen.findByText(tr.milestone.noFeedback);
		expect(
			screen.queryByRole("button", { name: tr.milestone.printReport }),
		).toBeNull();
	});

	it("prints group summaries when detailed feedback is disabled", async () => {
		mocks.getAdminSettings.mockResolvedValue({
			data: { hide_milestone_feedback: true },
		});
		const report = await printReport();
		expect(report).toContain(tr.milestone.reportTitle);
		expect(report).toContain("Emma");
		expect(report).toContain("Movement");
		expect(report).toContain(tr.milestone.recommendWatch);
		expect(report).not.toContain("undefined");
	});

	it("prints groups with no detailed entries even when details are enabled", async () => {
		const report = await printReport();
		expect(report).toContain("Movement");
		expect(alertStore.isAlertShown).toBe(false);
	});

	it("still includes negative milestone feedback and filters positive feedback", async () => {
		mocks.getDetailedFeedbackForAnswersession.mockResolvedValue({
			data: { 10: { 100: -1, 101: 1 } },
		});
		const report = await printReport();
		expect(report).toContain("Walking");
		expect(report).toContain(tr.milestone.recommendHelpShort);
		expect(report).not.toContain("Running");
	});

	it("aborts on a historical feedback load failure and can retry", async () => {
		render(FeedbackPage);
		const button = await screen.findByRole("button", {
			name: tr.milestone.printReport,
		});
		mocks.getCompletedMilestoneAnswerSessions.mockResolvedValue({
			data: { ...sessions, 2: { id: 2, created_at: "2020-01-01T00:00:00Z" } },
		});
		mocks.getDetailedFeedbackForAnswersession.mockImplementation(
			async ({ path }) =>
				path.answersession_id === 2
					? { error: { detail: "Failed" } }
					: { data: {} },
		);
		await fireEvent.click(button);
		await waitFor(() => expect(printWindow.close).toHaveBeenCalledOnce());
		expect(printWindow.print).not.toHaveBeenCalled();
		expect(printWindow.document.write).not.toHaveBeenCalled();
		expect(alertStore.message).toBe(tr.milestone.feedbackLoadingError);

		mocks.getDetailedFeedbackForAnswersession.mockResolvedValue({ data: {} });
		await fireEvent.click(button);
		await waitFor(() => expect(printWindow.print).toHaveBeenCalledOnce());
		expect(printWindow.document.write.mock.calls[0][0]).toContain("1-1-2020");
	});

	it("opens the print window before waiting for report data", async () => {
		render(FeedbackPage);
		const button = await screen.findByRole("button", {
			name: tr.milestone.printReport,
		});
		let resolveReport!: (value: { data: typeof sessions }) => void;
		mocks.getCompletedMilestoneAnswerSessions.mockReturnValue(
			new Promise((resolve) => {
				resolveReport = resolve;
			}),
		);
		await fireEvent.click(button);
		expect(window.open).toHaveBeenCalledOnce();
		expect(printWindow.print).not.toHaveBeenCalled();
		resolveReport({ data: sessions });
		await waitFor(() => expect(printWindow.print).toHaveBeenCalledOnce());
	});
});
