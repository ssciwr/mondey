import { waitLocale } from 'svelte-i18n';
import { client } from '$lib/client/services.gen';

export const prerender = true;

client.setConfig({
	baseUrl: import.meta.env.VITE_MONDEY_API_URL
});

export async function load() {
	await waitLocale();
}
