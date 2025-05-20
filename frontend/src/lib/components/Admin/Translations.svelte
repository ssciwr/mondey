<svelte:options runes={true} />

<script lang="ts">
import { updateI18N } from "$lib/client/sdk.gen";
import EditTranslationModal from "$lib/components/Admin/EditTranslationModal.svelte";
import InputAutoTranslate from "$lib/components/Admin/InputAutoTranslate.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import type { Translation } from "$lib/i18n.svelte";
import { translationIds } from "$lib/translations";
import { Accordion, AccordionItem, Card, Label } from "flowbite-svelte";
import { onMount } from "svelte";

let translations: Record<string, Translation> = $state(
	{} as Record<string, Translation>,
);

let missing_translations: Array<string> = $state([] as Array<string>);
let open_edit_translation_modal = $state(false);

async function getTranslations() {
	await i18n.load();
	let missing_translations_set: Set<string> = new Set();
	for (const locale of i18n.locales) {
		try {
			const res = await fetch(
				`${import.meta.env.VITE_MONDEY_API_URL}/static/i18n/${locale}.json`,
				{ cache: "no-cache" },
			);
			let data = {} as Translation;
			if (!res.ok) {
				console.log(
					`Failed to fetch locale ${locale} with status ${res.status}`,
				);
			} else {
				data = await res.json();
			}
			// ensure all section keys are present, if not create them
			for (const section_key in translationIds) {
				if (!(section_key in data)) {
					data[section_key] = {};
				}
			}
			for (const [section_key, section] of Object.entries(translationIds)) {
				for (const [item_key, item] of Object.entries(section)) {
					if (
						!(item_key in data[section_key]) ||
						data[section_key][item_key] === ""
					) {
						if (locale === "de") {
							// use built-in frontend text for any missing / empty entries in de locale json from server
							data[section_key][item_key] = item;
						} else {
							// otherwise add to list of missing translations
							data[section_key][item_key] = "";
							missing_translations_set.add(`${section_key}.${item_key}`);
						}
					}
				}
			}
			translations[locale] = data;
		} catch {
			console.log(`Failed to fetch locale ${locale}`);
			translations[locale] = translationIds;
		}
	}
	missing_translations = Array.from(missing_translations_set);
	open_edit_translation_modal = missing_translations.length > 0;
}

async function saveChanges() {
	for (const lang_id of Object.keys(translations)) {
		const { data, error } = await updateI18N({
			body: translations[lang_id],
			path: {
				language_id: lang_id,
			},
		});
		if (error) {
			console.log(error);
			return;
		}
		console.log(data);
	}
	await getTranslations();
}

onMount(() => getTranslations());
</script>

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{i18n.tr.admin.translations}</h3>
<Accordion flush>
	{#each Object.entries(translationIds) as [section_key, section]}
		<AccordionItem>
			<span slot="header" class="flex gap-2 text-base">
				{section_key}
			</span>
			{#each Object.keys(section) as item_key}
				<div class="m-2 mb-4 rounded-md border p-2">
					<Label class="mb-2">{item_key}</Label>
					{#each i18n.locales as lang}
						<div class="mb-1">
							<InputAutoTranslate bind:value={translations[lang][section_key][item_key]} locale={lang} de_text={translations["de"][section_key][item_key]}/>
						</div>
					{/each}
				</div>
			{/each}
			<div class="my-2 content-center">
				<SaveButton onclick={saveChanges} />
			</div>
		</AccordionItem>
	{/each}
</Accordion>

<EditTranslationModal bind:open={open_edit_translation_modal} bind:translations={translations} missing_translations={missing_translations} onsave={saveChanges}/>
