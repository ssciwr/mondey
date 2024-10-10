<svelte:options runes={true} />

<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Card,
		Select
	} from 'flowbite-svelte';
	import ISO6391 from 'iso-639-1';
	import { _ } from 'svelte-i18n';
	import type { SelectOptionType } from 'flowbite-svelte';
	import { getTranslations } from '$lib/i18n';
	import { languages } from '$lib/stores/langStore';
	import DeleteModal from '$lib/components/Admin/DeleteModal.svelte';
	import AddButton from '$lib/components/Admin/AddButton.svelte';
	import DeleteButton from '$lib/components/Admin/DeleteButton.svelte';
	import { createLanguage, deleteLanguage } from '$lib/client/services.gen';

	const langCodes = ISO6391.getAllCodes();
	const langNames = ISO6391.getAllNativeNames();
	const langItems = langCodes.map((k, i) => {
		return { value: k, name: langNames[i] };
	}) as SelectOptionType<string>[];

	let selectedLang: string = $state('');
	let currentLanguageId: string = $state('');
	let showDeleteModal: boolean = $state(false);

	async function createLanguageAndUpdateLanguages() {
		const { data, error } = await createLanguage({ body: { lang: selectedLang } });
		if (error) {
			console.log(error);
		} else {
			console.log(data);
			await getTranslations();
		}
	}

	async function deleteLanguageAndUpdateLanguages() {
		const { data, error } = await deleteLanguage({
			path: { language_id: Number(currentLanguageId) }
		});
		if (error) {
			console.log(error);
		} else {
			console.log(data);
			await getTranslations();
		}
	}
</script>

<Card size="xl" class="m-5">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{$_('admin.languages')}</h3>
	<Table>
		<TableHead>
			<TableHeadCell>Code (ISO 639-1)</TableHeadCell>
			<TableHeadCell>Name</TableHeadCell>
			<TableHeadCell>Actions</TableHeadCell>
		</TableHead>
		<TableBody>
			{#each Object.entries($languages) as [lang, lang_id]}
				<TableBodyRow>
					<TableBodyCell>
						{lang}
					</TableBodyCell>
					<TableBodyCell>
						{ISO6391.getNativeName(lang)}
					</TableBodyCell>
					<TableBodyCell>
						<DeleteButton
							onclick={() => {
								currentLanguageId = lang_id;
								showDeleteModal = true;
							}}
						/>
					</TableBodyCell>
				</TableBodyRow>
			{/each}
			<TableBodyRow>
				<TableBodyCell></TableBodyCell>
				<TableBodyCell>
					<Select
						class="mt-2"
						items={langItems}
						bind:value={selectedLang}
						placeholder="Select a language..."
					/>
				</TableBodyCell>
				<TableBodyCell>
					<AddButton onclick={createLanguageAndUpdateLanguages} disabled={selectedLang === ''} />
				</TableBodyCell>
			</TableBodyRow>
		</TableBody>
	</Table>
</Card>

<DeleteModal bind:open={showDeleteModal} onclick={deleteLanguageAndUpdateLanguages}></DeleteModal>
