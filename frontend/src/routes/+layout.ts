import { client } from "$lib/client/client.gen";
export const prerender = true;

const apiUrl = import.meta.env.VITE_MONDEY_API_URL;

client.setConfig({
	baseUrl: apiUrl,
});
