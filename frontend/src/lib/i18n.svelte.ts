import { getLanguages } from "$lib/client";
import { user } from "$lib/stores/userStore.svelte";
import { translationIds } from "$lib/translations";

export type Translation = typeof translationIds;

function createI18n() {
	const translations: Record<string, Translation> = $state({
		de: translationIds,
	});
	let currentLocale = $state("de");
	let locales = $state(["de"] as Array<string>);
	const idLocale = "[ids]";
	return {
		get tr(): Translation {
			return translations[currentLocale];
		},
		get locale(): string {
			return currentLocale === idLocale ? "de" : currentLocale;
		},
		get selectedLocale(): string {
			return currentLocale;
		},
		set locale(locale: string) {
			if (locales.includes(locale)) {
				currentLocale = locale;
			}
		},
		get locales(): Array<string> {
			return locales;
		},
		load: async () => {
			const { data, error } = await getLanguages();
			if (!error && data) {
				locales = data;
				for (const locale of locales) {
					try {
						const res = await fetch(
							`${import.meta.env.VITE_MONDEY_API_URL}/static/i18n/${locale}.json`,
						);
						if (!res.ok) {
							console.log(
								`Failed to fetch locale ${locale} with status ${res.status}`,
							);
							translations[locale] = translationIds;
						} else {
							translations[locale] = await res.json();
						}
					} catch {
						console.log(`Failed to fetch locale ${locale}`);
					}
				}
				if (user?.data?.is_superuser) {
					// add ids to locales for admin users
					locales.push(idLocale);
					translations[idLocale] = {};
					for (const [section_key, section] of Object.entries(translationIds)) {
						translations[idLocale][section_key] = {};
						for (const item_key of Object.keys(section)) {
							translations[idLocale][section_key][item_key] =
								`[${section_key}.${item_key}]`;
						}
					}
				}
			}
		},
	};
}

export const i18n = createI18n();
