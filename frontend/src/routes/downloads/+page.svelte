<svelte:options runes={true} />

<script lang="ts">
import { getPublicDocuments } from "$lib/client/sdk.gen";
import type { DocumentPublic } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { translationIds } from "$lib/translations";
import { Button, Card } from "flowbite-svelte";
import DownloadOutline from "flowbite-svelte-icons/DownloadOutline.svelte";
import { onMount } from "svelte";

let documents = $state([] as DocumentPublic[]);
const downloadsText = $derived(i18n.tr.downloads ?? translationIds.downloads);

async function loadDocuments() {
	const { data, error } = await getPublicDocuments();
	if (error || !data) {
		console.error("Failed to load documents:", error);
		return;
	}
	documents = data;
}

onMount(() => {
	loadDocuments();
});
</script>

<svelte:head>
    <title>{downloadsText.pageTitle} - MONDEY</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
    <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">{downloadsText.pageTitle}</h1>
        <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {downloadsText.pageDescription}
        </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each documents as document}
            <Card class="h-full flex flex-col" data-testid={document.title}>
                <div class="flex-1">
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                        <b>{document.title}</b>
                    </h3>
                    <p class="text-gray-600 dark:text-gray-300 mb-4 flex-1">
                        {document.description}
                    </p>
                </div>
                <div class="mt-auto">
                    <Button
                            href={`${import.meta.env.VITE_MONDEY_API_URL}/static/documents/${document.id}.pdf`}
                            download={`${document.filename}`}
                            target="_blank"
                            class="w-full"
                            color="blue"
                    >
                        <DownloadOutline class="w-4 h-4 mr-2" />
                        {downloadsText.downloadButton}
                    </Button>
                </div>
            </Card>
        {:else}
            <div class="col-span-full text-center py-12">
                <p class="text-gray-500 dark:text-gray-400 text-lg">
                    {downloadsText.noDocumentsAvailable}
                </p>
            </div>
        {/each}
    </div>
</div>
