import type { ChildSummaryPublic } from "$lib/client/types.gen";

export function preventDefault(fn: (event: Event) => void) {
	return function (this: unknown, event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

// The API only tells us whether a child has an image (`has_image`); the image
// itself is fetched separately and attached client-side as an object URL.
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
