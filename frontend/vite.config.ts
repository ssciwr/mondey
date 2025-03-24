import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	const config = {
		plugins: [sveltekit(), svelteTesting()],
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
			port: 5173, // safe default and resolves type issue below
		},
	};

	if (process.env.PLAYWRIGHT) {
		config.server.port = 5173;
	} else {
		// config.server.port = 5173;
	}

	console.log(
		"During server set up, process.env.playwright was: ",
		process.env.PLAYWRIGHT,
	);

	return config;
});
