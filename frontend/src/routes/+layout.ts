import { client } from "$lib/client/services.gen";
export const prerender = true;

client.setConfig({
	baseUrl: import.meta.env.VITE_MONDEY_API_URL,
});
