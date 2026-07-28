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
