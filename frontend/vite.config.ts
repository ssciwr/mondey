import adapter from "@sveltejs/adapter-static";
import { sveltekit } from "@sveltejs/kit/vite";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";
import tailwindcss from "@tailwindcss/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, ".", "VITE_");
	const host = env.VITE_HOST || "localhost";
	const port = Number.parseInt(env.VITE_PORT || "5173", 10);
	const apiUrl = env.VITE_API_PROXY_URL || "http://localhost:8000";

	return {
		plugins: [
			tailwindcss(),
			sveltekit({
				preprocess: vitePreprocess(),
				adapter: adapter({
					pages: "build",
					assets: "build",
					fallback: "index.html",
					precompress: false,
					strict: true,
				}),
				paths: {
					base: process.argv.includes("dev")
						? ""
						: (process.env.BASE_PATH as "" | `/${string}` | undefined),
				},
			}),
			svelteTesting(),
		],
		test: {
			include: ["src/**/*.{test,spec}.{js,ts}"],
			environment: "jsdom",
			setupFiles: ["src/vitest-setup.ts"],
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
