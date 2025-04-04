import { client } from "$lib/client/client.gen";
export const prerender = true;

client.setConfig({
	baseUrl: import.meta.env.VITE_MONDEY_API_URL,
});
