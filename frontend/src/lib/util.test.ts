import { clearHiddenAnswers, isQuestionVisible } from "$lib/util";
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
