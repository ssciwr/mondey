import typographyPlugin from "@tailwindcss/typography";
import flowbitePlugin from "flowbite/plugin";

import type { Config } from "tailwindcss";

export default {
	content: [
		"./src/**/*.{html,js,svelte,ts}",
		"./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}",
	],
	darkMode: "selector",
	// ensure svelte compiler doesn't optimize these away if it doesn't realise we are using them
	safelist: [
		"bg-milestone-answer-0",
		"bg-milestone-answer-1",
		"bg-milestone-answer-2",
		"bg-milestone-answer-3",
	],
	theme: {
		extend: {
			colors: {
				// flowbite-svelte
				primary: {
					50: "#DDE1ED",
					100: "#D5D9E9",
					200: "#BAC1DA",
					300: "#9AA5C9",
					400: "#8592BE",
					500: "#6C7BB0",
					600: "#5D6EA8",
					700: "#556499",
					800: "#4D5B8B",
					900: "#46537E",
				},

				"additional-color": {
					50: "#E2F1F0",
					100: "#D5EAE9",
					200: "#C7E3E2",
					300: "#B6DBDA",
					400: "#A5D2D1",
					500: "#96BFBE",
					600: "#7C9E9D",
					700: "#698584",
					800: "#556C6B",
					900: "4D6261",
				},

				"milestone-answer": {
					0: "#f2e8cf",
					1: "#cdd993",
					2: "#a7c957",
					3: "#6a994e",
				},
				feedback: {
					0: "#98CB6A",
					1: "#FFCA67",
					2: "#E9715F",
				},
			},
			fontSize: {
				xs: ".75rem",
				sm: ".875rem",
				base: "1rem",
				lg: "1.125rem",
				xl: "1.25rem",
				"2xl": "1.5rem",
				"3xl": "1.875rem",
				"4xl": "2.25rem",
				"5xl": "3rem",
				"6xl": "4rem",
				"7xl": "5rem",
			},
		},
	},

	plugins: [flowbitePlugin, typographyPlugin],
} as Config;
