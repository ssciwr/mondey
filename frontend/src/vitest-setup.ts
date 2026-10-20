// jsdom does not implement the dialog element methods used by flowbite-svelte Modals
HTMLDialogElement.prototype.showModal = function () {
	this.open = true;
};
HTMLDialogElement.prototype.show = function () {
	this.open = true;
};
HTMLDialogElement.prototype.close = function () {
	this.open = false;
};

// jsdom also does not implement the Web Animations API used by svelte transitions
Element.prototype.animate = () => {
	const animation = {
		playState: "finished",
		effect: null,
		onfinish: () => {},
		cancel: () => {},
	};
	setTimeout(() => animation.onfinish());
	return animation as unknown as Animation;
};
