import type { ThemeConfig } from "flowbite-svelte";

// Overrides of the flowbite-svelte default component classes
export const flowbiteTheme: ThemeConfig = {
	card: { base: "p-4 sm:p-6 text-gray-500 dark:text-gray-400" },
	tabs: { base: "flex-wrap" },
	// full width textareas (the class of an unwrapped textarea can't be set via the theme, so it is set via its parent div)
	textarea: { div: "w-full *:block *:w-full" },
};
