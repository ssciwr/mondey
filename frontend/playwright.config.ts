import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
	testDir: "./tests",
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: "html",
	use: {
		baseURL: "http://localhost:5173",
		trace: "on-first-retry",
	},
	projects: [
		{
			name: "chromium",
			use: { ...devices["Desktop Chrome"] },
		},

		{
			name: "firefox",
			use: { ...devices["Desktop Firefox"] },
		},

		// {
		// 	name: "webkit",
		// 	use: { ...devices["Desktop Safari"] },
		// },
		{
			name: "Mobile Chrome",
			use: { ...devices["Pixel 5"] },
			testIgnore: [/.*admin.*\.spec\.ts/],
		},
		// {
		// 	name: "Mobile Safari",
		// 	use: { ...devices["iPhone 12"] },
		// },
	],
	webServer: {
		command: process.env.CI
			? `pnpm exec ws --port 5173 --directory build --spa index.html --rewrite '/api/(.*) -> http://localhost:8000/api/$1'` // this should all match the below...
			: "pnpm exec vite dev --port 5173",
		port: 5173,
		reuseExistingServer: !process.env.CI,
		env: {
			...process.env,
			VITE_MONDEY_API_URL: "http://localhost:5173/api",
			VITE_API_PROXY_URL: "http://localhost:8000",
			VITE_HOST: "localhost", // these should be the defaults anyway...
			VITE_PORT: 5173,
		},
	},
});
