<svelte:options runes={true} />

<script lang="ts">
import { updateI18N } from "$lib/client/services.gen";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { getI18nJson, getTranslations } from "$lib/i18n";
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
import { _, locales } from "svelte-i18n";
import de from "../../../locales/de.json";

type Translation = Record<string, Record<string, string>>;
let translations = $state({} as Record<string, Translation>);

function fillMissingSections(translation: Translation): Translation {
	for (const section_key in de) {
		if (!(section_key in translation)) {
			translation[section_key] = {};
		}
	}
	return translation;
}

async function refreshTranslations() {
	for (const lang_id of $locales) {
		if (lang_id !== "de") {
			translations[lang_id] = fillMissingSections(await getI18nJson(lang_id));
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

onMount(() => refreshTranslations());
</script>

<Card size="xl" class="m-5">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{$_('admin.translations')}</h3>
	<Accordion flush>
		{#each Object.entries(de) as [section_key, section]}
			<AccordionItem>
				<span slot="header" class="flex gap-2 text-base">
					{section_key}
				</span>
				{#each Object.entries(section) as [item_key, item]}
					<div class="m-2 mb-4 rounded-md border p-2">
						<Label class="mb-2">{item_key}</Label>
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<InputAddon>de</InputAddon>
								<p class="w-full rounded-r-md border px-2">{item}</p>
							</ButtonGroup>
						</div>
						{#each Object.keys(translations) as lang}
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
