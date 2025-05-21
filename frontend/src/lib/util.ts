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
