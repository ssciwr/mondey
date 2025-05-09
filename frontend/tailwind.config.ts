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
		"bg-milestone-answer--1",
	],
	theme: {
		extend: {
			colors: {
				// From your original additional-color in CSS
				primary: {
					50: "#E2F1F0",
					100: "rgb(50,50,50)",
					200: "#C7E3E2",
					300: "#B6DBDA",
					400: "#A5D2D1",
					500: "#96BFBE",
					600: "#89b3b2",
					700: "#7C9E9D", // This is rgb(124, 158, 157)
					800: "#556C6B",
					900: "#4D6261",
				},

				"additional-color": {
					50: "#E2F1F0",
					100: "#D5EAE9",
					200: "#C7E3E2",
					300: "#B6DBDA",
					400: "#A5D2D1",
					500: "#96BFBE",
					600: "#7C9E9D", // This is rgb(124, 158, 157)
					700: "#698584",
					800: "#556C6B",
					900: "#4D6261",
				},

				milestone: {
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

				// Custom colors for special backgrounds
				"special-bg": "rgba(124, 158, 157, 0.15)",
				"delete-bg": "rgba(200, 30, 30, 0.1)",
				"delete-hover": "rgba(200, 30, 30, 0.6)",

				"milestone-answer": {
					0: "#f2e8cf",
					1: "#cdd993",
					2: "#a7c957",
					3: "#6a994e",
					"-1": "#6C7BB0",
				},
				feedback: {
					0: "#98CB6A",
					1: "#F59C2F",
					2: "#E9715F",
				},
				"feedback-background": {
					0: "#b17a06",
				},
				"feedback-border": {
					0: "#f8c554",
				},
				red: {
					50: "rgb(255, 202, 202)",
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

	plugins: [
		flowbitePlugin,
		typographyPlugin,
		({ addComponents, theme }) => {
			addComponents({
				".btn": {
					cursor: "pointer",
					"transition-property": "all",
					"transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
					"transition-duration": "100ms",
				},
				".text-btn": {
					"padding-top": "0.5rem",
					"padding-bottom": "0.5rem",
					"padding-left": "1.25rem",
					"padding-right": "1.25rem",
					"border-radius": "0.375rem",
					"min-width": "12rem",
					margin: "0.25rem",
				},
				".btn-primary": {
					"@apply inline-flex items-center justify-center gap-2 text-white font-semibold bg-additional-color-600 rounded-lg shadow-md focus:outline-none focus:ring focus:ring-additional-color-300 focus:ring-opacity-75 text-btn":
						{},
					border: "2px solid rgb(124, 158, 157)",
					"background-color": "rgb(124, 158, 157)",
					"&:hover": {
						"bg-additional-color-700": {},
						border: "2px solid #556C6B!important;",
					},
				},
				".btn-secondary": {
					"@apply text-additional-color-700 inline-flex items-center justify-center gap-2 font-semibold rounded-lg shadow-md focus:outline-none focus:ring focus:ring-additional-color-300 focus:ring-opacity-75 text-btn text-additional-color-700":
						{},
					border: "2px solid rgb(124, 158, 157)",
					"background-color": "#e5f4f4!important",
					color: "#698584!important",
					"&:hover": {
						"background-color": "#96BFBE!important",
						border: "2px solid #96BFBE!important",
						color: "white!important",
					},
					"@apply dark:bg-special-bg dark:text-white": {},
				},
				".btn-danger": {
					"@apply inline-flex items-center justify-center gap-2 font-semibold rounded-lg shadow-md focus:outline-none focus:ring focus:ring-red-400 focus:ring-opacity-75 text-btn text-red-700":
						{},
					"background-color": "#e5f4f4!important",
					border: "2px solid rgb(124, 158, 157)",
					color: "rgba(200, 30, 30, 0.8)!important",
					"&:hover": {
						border: "2px solid rgb(240, 82, 82)",
						"background-color": "rgba(200, 30, 30, 0.3)!important",
						color: "rgba(200, 30, 30, 1)!important",
						"@apply text-white bg-red-500": {},
					},
					"@apply dark:text-white": {},
				},
				".bg-special": {
					"background-color": "rgba(124, 158, 157, 0.15)",
					color: "rgba(255, 255, 255, 0.925)",
				},
				// Make sure icons have consistent vertical alignment
				".btn-primary svg, .btn-secondary svg, .btn-danger svg": {
					"@apply inline-block align-middle": {},
				},
				// Media query for mobile responsiveness
				"@media only screen and (min-device-width: 320px) and (max-device-width: 480px)":
					{
						".btn": {
							"min-width": "100%",
						},
						".btn-icon": {
							"min-width": "unset",
						},
					},
			});
		},
	],
} as Config;
