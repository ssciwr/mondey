import { getLanguages } from "$lib/client";
import { user } from "$lib/stores/userStore.svelte";
import { translationIds } from "$lib/translations";

export type Translation = typeof translationIds;

export type TranslationSections = Record<string, Record<string, string>>;

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
			return locales.filter((loc) => {
				return loc !== idLocale;
			});
		},
		get selectableLocales(): Array<string> {
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
					translations[idLocale] = Object.fromEntries(
						Object.entries(translationIds).map(([section_key, section]) => [
							section_key,
							Object.fromEntries(
								Object.keys(section).map((item_key) => [
									item_key,
									`[${section_key}.${item_key}]`,
								]),
							),
						]),
					) as Translation;
				}
			}
		},
	};
}

export const i18n = createI18n();
