import { client } from "$lib/client/client.gen";
export const prerender = true;

const apiUrl = import.meta.env.VITE_MONDEY_API_URL;
console.log("Mondey API URL configured:", apiUrl);

client.setConfig({
	baseUrl: apiUrl,
});
