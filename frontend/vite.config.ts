import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	return {
		plugins: [sveltekit(), svelteTesting(), tailwindcss()],
		test: {
			include: ["src/**/*.{test,spec}.{js,ts}"],
			environment: "jsdom",
		},
		server: {
			host: "localhost",
			strictPort: true,
			proxy: {
				"/api": "http://localhost:8000",
			},
			port: 5173,
		},
		preview: {
			host: "localhost",
			strictPort: true,
			proxy: {
				"/api": "http://localhost:8000",
			},
			port: 5173,
		},
	};
});
