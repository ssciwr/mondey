import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, ".", "VITE_");
	const host = env.VITE_HOST || "localhost";
	const port = Number.parseInt(env.VITE_PORT || "5173", 10);
	const apiUrl = env.VITE_API_PROXY_URL || "http://localhost:8000";

	return {
		plugins: [sveltekit(), svelteTesting()],
		test: {
			include: ["src/**/*.{test,spec}.{js,ts}"],
			environment: "jsdom",
		},
		server: {
			host,
			strictPort: true,
			proxy: {
				"/api": apiUrl,
			},
			port,
		},
		preview: {
			host,
			strictPort: true,
			proxy: {
				"/api": apiUrl,
			},
			port,
		},
	};
});
