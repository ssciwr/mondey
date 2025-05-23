<svelte:options runes={true} />

<script lang="ts">
import { createLanguage, deleteLanguage } from "$lib/client/sdk.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import type { SelectOptionType } from "flowbite-svelte";
import {
	Card,
	Select,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import ISO6391 from "iso-639-1";

const langCodes = ISO6391.getAllCodes();
const langNames = ISO6391.getAllNativeNames();
const langItems = langCodes.map((k, i) => {
	return { value: k, name: langNames[i] };
}) as SelectOptionType<string>[];

let selectedLangId: string = $state("");
let currentLanguageId: string = $state("");
let showDeleteModal: boolean = $state(false);

async function createLanguageAndUpdateLanguages() {
	const { data, error } = await createLanguage({
		body: { id: selectedLangId },
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await i18n.load();
	}
}

async function deleteLanguageAndUpdateLanguages() {
	const { data, error } = await deleteLanguage({
		path: { language_id: currentLanguageId },
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await i18n.load();
	}
}
</script>

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{i18n.tr.admin.languages}</h3>
<Table>
	<TableHead>
		<TableHeadCell>Code (ISO 639-1)</TableHeadCell>
		<TableHeadCell>Name</TableHeadCell>
		<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
	</TableHead>
	<TableBody>
		{#each i18n.locales as lang_id}
			<TableBodyRow>
				<TableBodyCell>
					{lang_id}
				</TableBodyCell>
				<TableBodyCell>
					{ISO6391.getNativeName(lang_id)}
				</TableBodyCell>
				<TableBodyCell>
					{#if !['de', 'en'].includes(lang_id)}
						<DeleteButton
							onclick={() => {
								currentLanguageId = lang_id;
								showDeleteModal = true;
							}}
						/>
					{/if}
				</TableBodyCell>
			</TableBodyRow>
		{/each}
		<TableBodyRow>
			<TableBodyCell></TableBodyCell>
			<TableBodyCell>
				<Select
					class="mt-2"
					items={langItems}
					bind:value={selectedLangId}
					placeholder="Select a language..."
				/>
			</TableBodyCell>
			<TableBodyCell>
				<AddButton onclick={createLanguageAndUpdateLanguages} disabled={selectedLangId === ''} />
			</TableBodyCell>
		</TableBodyRow>
	</TableBody>
</Table>

<DeleteModal bind:open={showDeleteModal} onclick={deleteLanguageAndUpdateLanguages}></DeleteModal>
