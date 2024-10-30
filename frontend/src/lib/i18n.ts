import { getLanguages } from "$lib/client";
import { addMessages, init } from "svelte-i18n";
import de from "../locales/de.json";

export async function getI18nJson(lang_id: string) {
	try {
		const res = await fetch(
			`${import.meta.env.VITE_MONDEY_API_URL}/static/i18n/${lang_id}.json`,
		);
		if (!res.ok) {
			console.log(
				`getI18nJson failed for lang_id ${lang_id} with status ${res.status}, returning de translations`,
			);
			return de;
		}
		return await res.json();
	} catch {
		console.log(
			`getI18nJson failed for lang_id ${lang_id}, returning de translations`,
		);
		return de;
	}
}

async function getTranslation(lang_id: string) {
	const json = await getI18nJson(lang_id);
	addMessages(lang_id, json);
}

export async function getTranslations() {
	const { data, error } = await getLanguages();
	if (!error && data) {
		data.forEach((lang_id) => {
			if (lang_id !== "de") {
				getTranslation(lang_id);
			}
		});
	}
}

addMessages("de", de);
init({
	fallbackLocale: "de",
	initialLocale: "de",
});
