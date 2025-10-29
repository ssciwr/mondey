<svelte:options runes={true} />

<script lang="ts">
import {
	createDocument,
	deleteDocument,
	getDocuments,
	updateDocument,
} from "$lib/client/sdk.gen";
import type { DocumentAdmin } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import {
	Button,
	Card,
	Fileupload,
	Input,
	Label,
	Modal,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
	Textarea,
} from "flowbite-svelte";
import DownloadOutline from "flowbite-svelte-icons/DownloadOutline.svelte";
import { onMount } from "svelte";
import DangerousDeleteModal from "../DangerousDeleteModal.svelte";
import AddButton from "./AddButton.svelte";
import DeleteButton from "./DeleteButton.svelte";
import EditButton from "./EditButton.svelte";

let documents = $state([] as DocumentAdmin[]);
let showAddModal = $state(false);
let showEditModal = $state(false);
let showDeleteModal = $state(false);
let selectedDocument = $state(null as DocumentAdmin | null);
let uploadFile = $state(null as File | null);

let newDocument = $state({
	title: "",
	description: "",
});

let editDocument = $state({
	title: "",
	description: "",
});

async function loadDocuments() {
	const { data, error } = await getDocuments();
	if (error || !data) {
		alertStore.showAlert(
			i18n.tr.admin.error,
			i18n.tr.admin.documentError,
			true,
			false,
		);
		return;
	}
	documents = data;
}

async function uploadDocument() {
	if (!uploadFile) return;

	const { data, error } = await createDocument({
		body: {
			title: newDocument.title,
			description: newDocument.description,
			file: uploadFile,
		},
	});

	if (error) {
		alertStore.showAlert(
			i18n.tr.admin.error,
			i18n.tr.admin.documentUploadError,
			true,
			false,
		);
		return;
	}

	showAddModal = false;
	newDocument = { title: "", description: "" };
	uploadFile = null;
	await loadDocuments();
}

async function updateSelectedDocument() {
	if (!selectedDocument) return;

	const { data, error } = await updateDocument({
		path: { document_id: selectedDocument.id },
		body: {
			title: editDocument.title,
			description: editDocument.description,
			filename: selectedDocument.filename,
		},
	});

	if (error) {
		alertStore.showAlert(
			i18n.tr.admin.error,
			i18n.tr.admin.documentError,
			true,
			false,
		);
		return;
	}

	showEditModal = false;
	selectedDocument = null;
	await loadDocuments();
}

function openEditModal(document: DocumentAdmin) {
	selectedDocument = document;
	editDocument = {
		title: document.title,
		description: document.description,
	};
	showEditModal = true;
}

function openDeleteModal(document: DocumentAdmin) {
	selectedDocument = document;
	showDeleteModal = true;
}

onMount(() => {
	loadDocuments();
});
</script>

<div class="space-y-4">
	<div class="flex justify-between items-center">
		<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{i18n.tr.admin.documents}</h3>
		<AddButton onclick={() => showAddModal = true} />
	</div>

	<div class="overflow-x-scroll overflow-y-scroll" style="min-width: 100%;">
		<Table class="w-full" style="min-width: 100%;">
		<TableHead>
			<TableHeadCell>{i18n.tr.admin.title}</TableHeadCell>
			<TableHeadCell>{i18n.tr.admin.desc}</TableHeadCell>
			<TableHeadCell>{i18n.tr.admin.documentCreated}</TableHeadCell>
			<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
		</TableHead>
		<TableBody>
			{#each documents as document}
				<TableBodyRow>
					<TableBodyCell>{document.title} - <Button
							size="xs"
							color="blue"
							href="/api/documents/{document.id}/download"
							target="_blank"
							title={i18n.tr.admin.download}
							class="ml-2"
					>
						<DownloadOutline class="w-4 h-4 mr-1" />
						{i18n.tr.admin.download}
					</Button></TableBodyCell>
					<TableBodyCell>{document.description.length > 15 ? document.description.substring(0, 15) + '...' : document.description}</TableBodyCell>
					<TableBodyCell>{new Date(document.created_at).toLocaleDateString()}</TableBodyCell>
					<TableBodyCell>
						<EditButton onclick={() => openEditModal(document)} />
						<DeleteButton onclick={() => openDeleteModal(document)} />
					</TableBodyCell>
				</TableBodyRow>
			{:else}
				<TableBodyRow>
					<TableBodyCell colspan="5" class="text-center text-gray-500">
						{i18n.tr.admin.noDocumentsFound}
					</TableBodyCell>
				</TableBodyRow>
			{/each}
		</TableBody>
		</Table>
	</div>
</div>

<Modal bind:open={showAddModal} title={i18n.tr.admin.uploadDocument}>
	<div class="space-y-4">
		<div>
			<Label for="title">{i18n.tr.admin.title}</Label>
			<Input id="title" bind:value={newDocument.title} />
		</div>
		<div>
			<Label for="description">{i18n.tr.admin.desc}</Label>
			<Textarea id="description" bind:value={newDocument.description} />
		</div>
		<div>
			<Label for="file">{i18n.tr.admin.pdfFile}</Label>
			<Fileupload
				id="file"
				accept=".pdf"
				onchange={(e) => uploadFile = e.target.files?.[0] || null}
			/>
		</div>
	</div>
	<svelte:fragment slot="footer">
		<Button color="green" disabled={!uploadFile || !newDocument.title} onclick={uploadDocument}>
			{i18n.tr.admin.upload}
		</Button>
		<Button color="alternative" onclick={() => showAddModal = false}>{i18n.tr.admin.cancel}</Button>
	</svelte:fragment>
</Modal>

<Modal bind:open={showEditModal} title={i18n.tr.admin.editDocument}>
	<div class="space-y-4">
		<div>
			<Label for="edit-title">{i18n.tr.admin.title}</Label>
			<Input id="edit-title" bind:value={editDocument.title} />
		</div>
		<div>
			<Label for="edit-description">{i18n.tr.admin.desc}</Label>
			<Textarea id="edit-description" bind:value={editDocument.description} />
		</div>
	</div>
	<svelte:fragment slot="footer">
		<Button color="green" onclick={updateSelectedDocument}>{i18n.tr.admin.update}</Button>
		<Button color="alternative" onclick={() => showEditModal = false}>{i18n.tr.admin.cancel}</Button>
	</svelte:fragment>
</Modal>

<DangerousDeleteModal
	bind:open={showDeleteModal}
	deleteDryRunnableRequest={(dry_run) => {
		if (dry_run) {
			return Promise.resolve({
				data: {
					ok: true,
					dry_run: true,
					children: { "documents": 1 },
					error: null
				}
			});
		}
		return deleteDocument({
			path: { document_id: selectedDocument?.id ?? 0 }
		});
	}}
	afterDelete={async () => {
		selectedDocument = null;
		await loadDocuments();
	}}
	intendedConfirmCode={selectedDocument?.filename ?? ""}
/>
