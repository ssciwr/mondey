export function preventDefault(fn: (event: Event) => void) {
	return function (event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

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
