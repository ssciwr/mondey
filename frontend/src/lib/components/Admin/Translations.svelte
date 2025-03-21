<svelte:options runes={true} />

<script lang="ts">
import { updateI18N } from "$lib/client/services.gen";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import type { Translation } from "$lib/tr.svelte";
import { translationIds } from "$lib/translations";
import {
	Accordion,
	AccordionItem,
	ButtonGroup,
	Card,
	Input,
	InputAddon,
	Label,
} from "flowbite-svelte";
import { onMount } from "svelte";

let translations: Record<string, Translation> = $state(
	{} as Record<string, Translation>,
);

async function getTranslations() {
	await i18n.load();
	for (const locale of i18n.locales) {
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
				let data = await res.json();
				// ensure all section keys are present, if not create them
				for (const section_key in translationIds) {
					if (!(section_key in data)) {
						data[section_key] = {};
					}
				}
				// use built-in frontend text for any missing / empty entries in de locale json from server
				if (locale === "de") {
					for (const [section_key, section] of Object.entries(translationIds)) {
						for (const [item_key, item] of Object.entries(section)) {
							if (
								!(item_key in data[section_key]) ||
								data[section_key][item_key] === ""
							) {
								console.log(section_key, item_key);
								data[section_key][item_key] = item;
							}
						}
					}
				}
				translations[locale] = data;
			}
		} catch {
			console.log(`Failed to fetch locale ${locale}`);
			translations[locale] = translationIds;
		}
	}
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

<Card size="xl" class="m-5">
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
								<ButtonGroup class="w-full">
									<InputAddon>{lang}</InputAddon>
									<Input bind:value={translations[lang][section_key][item_key]} />
								</ButtonGroup>
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
</Card>
