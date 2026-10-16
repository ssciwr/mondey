import {
	answerSessionIdsNewestFirst,
	clearHiddenAnswers,
	isCurrentAnswerSession,
	isQuestionVisible,
	overallFeedback,
} from "$lib/util";
import { describe, expect, it } from "vitest";

describe("isQuestionVisible", () => {
	it("is visible when it has no parent question", () => {
		const question = {
			id: 1,
			depends_on_question_id: null,
			show_if_answer: "",
		};
		expect(isQuestionVisible(question, {})).toBe(true);
	});

	it("is visible when the parent answer matches a single trigger", () => {
		const question = {
			id: 2,
			depends_on_question_id: 1,
			show_if_answer: "yes",
		};
		const answers = { 1: { answer: "yes" } };
		expect(isQuestionVisible(question, answers)).toBe(true);
	});

	it("is hidden when the parent answer does not match", () => {
		const question = {
			id: 2,
			depends_on_question_id: 1,
			show_if_answer: "yes",
		};
		const answers = { 1: { answer: "no" } };
		expect(isQuestionVisible(question, answers)).toBe(false);
	});

	it("is hidden when the parent has no answer yet", () => {
		const question = {
			id: 2,
			depends_on_question_id: 1,
			show_if_answer: "yes",
		};
		expect(isQuestionVisible(question, {})).toBe(false);
		expect(isQuestionVisible(question, { 1: { answer: "" } })).toBe(false);
	});

	it("matches any of several ';'-separated triggers", () => {
		const question = {
			id: 2,
			depends_on_question_id: 1,
			show_if_answer: "a;b;c",
		};
		expect(isQuestionVisible(question, { 1: { answer: "b" } })).toBe(true);
		expect(isQuestionVisible(question, { 1: { answer: "d" } })).toBe(false);
	});

	it("matches when a multi-select parent answer includes a trigger", () => {
		const question = {
			id: 2,
			depends_on_question_id: 1,
			show_if_answer: "a;b",
		};
		expect(isQuestionVisible(question, { 1: { answer: ["x", "b"] } })).toBe(
			true,
		);
		expect(isQuestionVisible(question, { 1: { answer: ["x", "y"] } })).toBe(
			false,
		);
	});

	it("is visible when a parent is set but no trigger values are configured", () => {
		const question = { id: 2, depends_on_question_id: 1, show_if_answer: "" };
		expect(isQuestionVisible(question, { 1: { answer: "no" } })).toBe(true);
	});
});

describe("clearHiddenAnswers", () => {
	it("clears the answer of a hidden dependent question", () => {
		const questions = [
			{ id: 1, depends_on_question_id: null, show_if_answer: "" },
			{ id: 2, depends_on_question_id: 1, show_if_answer: "yes" },
		];
		const answers = {
			1: { answer: "no", additional_answer: "" },
			2: { answer: "some value", additional_answer: "extra" },
		};
		const changed = clearHiddenAnswers(questions, answers);
		expect(changed).toBe(true);
		expect(answers[2].answer).toBe("");
		expect(answers[2].additional_answer).toBe("");
	});

	it("leaves visible questions untouched", () => {
		const questions = [
			{ id: 1, depends_on_question_id: null, show_if_answer: "" },
			{ id: 2, depends_on_question_id: 1, show_if_answer: "yes" },
		];
		const answers = {
			1: { answer: "yes", additional_answer: "" },
			2: { answer: "some value", additional_answer: "" },
		};
		const changed = clearHiddenAnswers(questions, answers);
		expect(changed).toBe(false);
		expect(answers[2].answer).toBe("some value");
	});

	it("does not report a change when the hidden answer is already empty", () => {
		const questions = [
			{ id: 1, depends_on_question_id: null, show_if_answer: "" },
			{ id: 2, depends_on_question_id: 1, show_if_answer: "yes" },
		];
		const answers = {
			1: { answer: "no", additional_answer: "" },
			2: { answer: "", additional_answer: "" },
		};
		expect(clearHiddenAnswers(questions, answers)).toBe(false);
	});
});

describe("answerSessionIdsNewestFirst", () => {
	it("sorts ids numerically, newest first", () => {
		const sessions = { 9: {}, 98: {}, 102: {}, 1000: {} };
		expect(answerSessionIdsNewestFirst(sessions)).toEqual([1000, 102, 98, 9]);
	});

	it("returns an empty list for no sessions", () => {
		expect(answerSessionIdsNewestFirst({})).toEqual([]);
	});
});

describe("overallFeedback", () => {
	it("is the lowest group feedback", () => {
		expect(overallFeedback({ 1: 1, 2: 1 })).toBe(1);
		expect(overallFeedback({ 1: 1, 2: 0 })).toBe(0);
		expect(overallFeedback({ 1: 1, 2: 0, 3: -1 })).toBe(-1);
	});

	it("ignores groups with not enough data", () => {
		expect(overallFeedback({ 1: -2, 2: -1, 3: 1 })).toBe(-1);
		expect(overallFeedback({ 1: -2, 2: 0 })).toBe(0);
		expect(overallFeedback({ 1: -2, 2: 1 })).toBe(1);
	});

	it("is not enough data if no group has enough data", () => {
		expect(overallFeedback({ 1: -2, 2: -2 })).toBe(-2);
		expect(overallFeedback({})).toBe(-2);
	});
});

describe("isCurrentAnswerSession", () => {
	// UTC times, so the test does not depend on daylight saving time in the local time zone
	const now = new Date("2026-10-16T12:00:00Z");

	it("is current if less than three weeks old", () => {
		expect(isCurrentAnswerSession("2026-10-16T09:00:00Z", now)).toBe(true);
		expect(isCurrentAnswerSession("2026-09-26T12:00:01Z", now)).toBe(true);
	});

	it("is not current if three weeks or older", () => {
		expect(isCurrentAnswerSession("2026-09-25T12:00:00Z", now)).toBe(false);
		expect(isCurrentAnswerSession("2025-05-14T12:00:00Z", now)).toBe(false);
	});
});
