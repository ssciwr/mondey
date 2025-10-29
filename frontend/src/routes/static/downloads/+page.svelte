<svelte:options runes={true} />

<script lang="ts">
import { getPublicDocuments } from "$lib/client/sdk.gen";
import type { DocumentPublic } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { Button, Card } from "flowbite-svelte";
import DownloadOutline from "flowbite-svelte-icons/DownloadOutline.svelte";
import { onMount } from "svelte";

const CENTRAL_API_BASE = "https://mondey.de/api";

let documents = $state([] as DocumentPublic[]);
let documentSource = $state<"central" | "local">("local");

async function loadDocuments() {
	try {
		const response = await fetch(`${CENTRAL_API_BASE}/documents/`);
		if (response.ok) {
			const data = await response.json();
			documents = data;
			documentSource = "central";
			return;
		}
	} catch (error) {
		console.log("Central server unavailable, falling back to local");
	}

	const { data, error } = await getPublicDocuments();
	if (error || !data) {
		console.error("Failed to load documents:", error);
		return;
	}
	documents = data;
	documentSource = "local";
}

onMount(() => {
	loadDocuments();
});
</script>

<svelte:head>
    <title>{i18n.tr.downloads.pageTitle} - MONDEY</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
    <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">{i18n.tr.downloads.pageTitle}</h1>
        <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {i18n.tr.downloads.pageDescription}
        </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each documents as document}
            <Card class="h-full flex flex-col">
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
                            href={documentSource === "central" ? `${CENTRAL_API_BASE}/documents/${document.id}/download` : `/api/documents/${document.id}/download`}
                            target="_blank"
                            class="w-full"
                            color="blue"
                    >
                        <DownloadOutline class="w-4 h-4 mr-2" />
                        {i18n.tr.downloads.downloadButton}
                    </Button>
                </div>
            </Card>
        {:else}
            <div class="col-span-full text-center py-12">
                <p class="text-gray-500 dark:text-gray-400 text-lg">
                    {i18n.tr.downloads.noDocumentsAvailable}
                </p>
            </div>
        {/each}
    </div>
</div>
