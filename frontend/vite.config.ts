import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import tailwindcss from "tailwindcss";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	return {
		plugins: [tailwindcss(), sveltekit(), svelteTesting()],
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
	};
});
