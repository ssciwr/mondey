import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
	input: "../mondey_backend/openapi.json",
	output: {
		path: "src/lib/client",
		format: "prettier",
	},
	plugins: ["@hey-api/client-fetch"],
});
