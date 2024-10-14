import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
	client: '@hey-api/client-fetch',
	input: '../mondey_backend/openapi.json',
	output: {
		path: 'src/lib/client',
		format: 'prettier'
	}
});
