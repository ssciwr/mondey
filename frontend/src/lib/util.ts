export function preventDefault(fn: (event: Event) => void) {
	return function (event: Event) {
		event.preventDefault();
		fn.call(this, event);
	};
}

export type EventHandler = (event: Event | undefined) => void | Promise<void>;
export type CardElement = {
	header: string | undefined | null;
	image: string | null;
	summary: string | null;
	events: { [key: string]: EventHandler };
};

export type CardStyle = {
	card: { [key: string]: string | boolean | null | undefined } | null;
	header: { [key: string]: string | boolean | null | undefined } | null;
	summary: { [key: string]: string | boolean | null | undefined } | null;
	button: { [key: string]: string | boolean | null | undefined } | null;
	progress: { [key: string]: string | boolean | null | undefined } | null;
	auxilliary: { [key: string]: string | boolean | null | undefined } | null;
};
