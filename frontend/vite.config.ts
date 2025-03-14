import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
	plugins: [sveltekit(), svelteTesting()],
	test: {
		include: ["src/**/*.{test,spec}.{js,ts}"],
		environment: "jsdom",
	},
	server: {
		host: "localhost",
		port: 5173,
		strictPort: true,
		proxy: {
			"/api": "http://localhost:8000",
		},
	},
});
