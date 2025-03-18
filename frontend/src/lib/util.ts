import type { Component } from "svelte";
export function preventDefault(fn: (event: Event) => void) {
	return function (event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

// Approximate, prefer tailwind CSS to this. From: https://stackoverflow.com/questions/11381673/detecting-a-mobile-browser
// Needs to be called from onMount because of window.
export function isMobile(): boolean {
	if (window === undefined) {
		throw new Error(
			"Run this function from onMount as it needs to access window.",
		);
	}
	const ViewportWidth = window.innerWidth;
	const ViewportHeight = window.innerHeight;

	const smallerEdgeSize = Math.min(ViewportWidth, ViewportHeight);
	const largerEdgeSize = Math.max(ViewportWidth, ViewportHeight);

	return smallerEdgeSize <= 480 && largerEdgeSize <= 896;
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
	color?: string | undefined;
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
