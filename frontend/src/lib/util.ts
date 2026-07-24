import type { ChildSummaryPublic } from "$lib/client/types.gen";

export function preventDefault(fn: (event: Event) => void) {
	return function (this: unknown, event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

export type ChildSummaryWithImage = ChildSummaryPublic & { image?: string };

export type PlotDatum = {
	age: number;
	[key: string]: number;
};

export type PlotData = {
	keys: Array<string>;
	data: Array<PlotDatum>;
};

export function isValidAge(value: number) {
	return Math.floor(value) === value && value >= 0 && value <= 72;
}

// Keep in sync with MIN_PASSWORD_LENGTH in the backend settings, which is what
// actually enforces this - the check here is only to give immediate feedback.
export const minPasswordLength = 12;

export function isValidPassword(password: string | null): boolean {
	return password !== null && password.length >= minPasswordLength;
}

type DependentQuestion = {
	id: number;
	depends_on_question_id?: number | null;
	show_if_answer?: string | null;
};

type QuestionAnswer = {
	answer?: string | string[] | null;
	additional_answer?: string | null;
};

/**
 * Whether a (possibly dependent) question should currently be shown, given the
 * current answers. A question with no `depends_on_question_id` is always shown.
 * A dependent question is shown only when the answer to its parent question
 * matches one of the ";"-separated values in `show_if_answer`. If no trigger
 * values are configured the question is treated as always shown.
 */
export function isQuestionVisible(
	question: DependentQuestion,
	answers: { [k: number]: QuestionAnswer },
): boolean {
	if (question.depends_on_question_id == null) {
		return true;
	}
	const triggers = (question.show_if_answer ?? "")
		.split(";")
		.filter((value) => value !== "");
	if (triggers.length === 0) {
		return true;
	}
	const parentAnswer = answers[question.depends_on_question_id]?.answer;
	if (Array.isArray(parentAnswer)) {
		return parentAnswer.some((value) => triggers.includes(value));
	}
	return parentAnswer != null && triggers.includes(parentAnswer);
}

/**
 * Reset the stored answer for any dependent question that is currently hidden,
 * so that stale/contradictory answers are not submitted. Mutates `answers` in
 * place and returns whether anything was changed.
 */
export function clearHiddenAnswers(
	questions: DependentQuestion[],
	answers: { [k: number]: QuestionAnswer },
): boolean {
	let changed = false;
	for (const question of questions) {
		const answer = answers[question.id];
		if (!answer || isQuestionVisible(question, answers)) {
			continue;
		}
		if (
			(answer.answer !== undefined &&
				answer.answer !== null &&
				answer.answer !== "") ||
			(answer.additional_answer !== undefined &&
				answer.additional_answer !== null &&
				answer.additional_answer !== "")
		) {
			answer.answer = "";
			answer.additional_answer = "";
			changed = true;
		}
	}
	return changed;
}
