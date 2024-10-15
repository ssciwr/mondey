<svelte:options runes={true} />

<script lang="ts">
	import {
		Accordion,
		AccordionItem,
		ButtonGroup,
		Card,
		Input,
		InputAddon,
		Label,
		P,
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { getI18nJson, getTranslations } from '$lib/i18n';
	import { languages } from '$lib/stores/langStore';
	import { updateI18N } from '$lib/client/services.gen';
	import SaveButton from '$lib/components/Admin/SaveButton.svelte';
	import de from '../../../locales/de.json';

	type Translation = Record<string, Record<string, string>>;
	let translations = $state({} as Record<string, Translation>);

	async function refreshTranslations() {
		for (const [lang, lang_id] of Object.entries($languages)) {
			if (lang !== 'de') {
				translations[lang] = await getI18nJson(lang_id);
			}
		}
	}

	async function saveChanges() {
		for (const lang of Object.keys(translations)) {
			const { data, error } = await updateI18N({
				body: translations[lang],
				path: {
					language_id: $languages[lang]
				}
			});
			if (error) {
				console.log(error);
				return;
			} else {
				console.log(data);
			}
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
