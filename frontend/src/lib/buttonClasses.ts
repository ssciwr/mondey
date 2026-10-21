/*
  Classes for the app's button styles, to be used as the class of a flowbite-svelte Button
  (the Button merges them with its own default classes, so they only need to set what differs from those)
*/
const base = "m-1 min-w-48 gap-2 border-2 border-primary-700 shadow-md";
const light = "bg-[#e5f4f4] dark:bg-[#e5f4f4]";

export const buttonClasses = {
	primary: `${base} hover:border-primary-800`,
	secondary: `${base} ${light} text-additional-color-700 hover:border-primary-500 hover:bg-primary-500 hover:text-white dark:hover:bg-primary-500`,
	danger: `${base} ${light} text-[#c81e1e]/80 hover:border-[#f05252] hover:bg-[#c81e1e]/30 hover:text-[#c81e1e] dark:hover:bg-[#c81e1e]/30`,
	// larger text, for the more prominent buttons
	large: "py-2 text-base font-semibold",
	// small square buttons with an icon, adjacent icon buttons form a button group (see app.css)
	icon: "btn-icon relative min-w-auto hover:z-1",
	// tooltips of the icon buttons
	tooltip: `${base} ${light} min-w-auto font-semibold text-additional-color-700 dark:text-additional-color-700`,
};
