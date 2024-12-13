import { getLanguages } from "$lib/client";
import { translationIds } from "$lib/translations";

export type Translation = typeof translationIds;

function createI18n() {
	const translations: Record<string, Translation> = $state({
		de: translationIds,
	});
	let currentLocale = $state("de");
	let locales = $state(["de"] as Array<string>);
	return {
		get tr(): Translation {
			return translations[currentLocale];
		},
		get locale(): string {
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
			}
		},
	};
}

export const i18n = createI18n();
