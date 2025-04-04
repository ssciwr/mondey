import type { Component } from "svelte";
export function preventDefault(fn: (event: Event) => void) {
	return function (event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

export type EventHandler = (event: Event | undefined) => void | Promise<void>;
export type CardElement = {
	header: string | undefined | null;
	summary: string | null | undefined;
	button?: any | undefined;
	href?: string | undefined;
	image?: string | undefined;
	progress?: number | undefined;
	events?: { [key: string]: EventHandler } | undefined;
	auxilliary?: any | undefined;
	buttonIcon?: Component | undefined;
	color?: string | null | undefined;
};

export type CardStyle = {
	card: { [key: string]: string | boolean | null | undefined } | null;
	header: { [key: string]: string | boolean | null | undefined } | null;
	summary: { [key: string]: string | boolean | null | undefined } | null;
	button?: { [key: string]: string | boolean | null | undefined } | null;
	progress?: {
		size: string | undefined;
		divClass: string | undefined;
		color: any;
		labelInsideClass: string | undefined;
		completeColor: any;
		labelInside: boolean | undefined;
	} | null;
	auxilliary?: { [key: string]: string | boolean | null | undefined } | null;
};

export type PlotDatum = {
	age: number;
	[key: string]: string | number;
};

export type PlotData = {
	keys: Array<string>;
	data: Array<PlotDatum>;
};
