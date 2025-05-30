import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	// Use Docker backend service in development when running in container
	// Check if we're running in Docker by looking for the DOCKER environment variable
	// or if the API URL is set to use the backend service
	const isDocker =
		process.env.VITE_MONDEY_API_URL === "/api" || process.env.DOCKER === "true";
	const apiTarget = isDocker ? "http://backend:80" : "http://localhost:8000";

	return {
		plugins: [sveltekit(), svelteTesting()],
		test: {
			include: ["src/**/*.{test,spec}.{js,ts}"],
			environment: "jsdom",
		},
		server: {
			host: "0.0.0.0", // Changed from localhost to 0.0.0.0 for Docker
			strictPort: true,
			proxy: {
				"/api": apiTarget,
			},
			port: 5173,
		},
		preview: {
			host: "0.0.0.0", // Changed from localhost to 0.0.0.0 for Docker
			strictPort: true,
			proxy: {
				"/api": apiTarget,
			},
			port: 5173,
		},
	};
});
