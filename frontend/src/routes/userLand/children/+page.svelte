<svelte:options runes={true}/>
<script lang="ts">
import { goto } from "$app/navigation";
import { getChildImage, getChildren } from "$lib/client/sdk.gen";
import type { ChildSummaryPublic } from "$lib/client/types.gen";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import ChildCardDisplay from "$lib/components/DataDisplay/ChildCardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { displayChildImages } from "$lib/features";
import { i18n } from "$lib/i18n.svelte.js";
import { alertStore } from "$lib/stores/alertStore.svelte.js";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { Heading, Spinner } from "flowbite-svelte";

let searchTerm = $state("");

async function setup(): Promise<ChildSummaryPublic[]> {
	const { data, error } = await getChildren();
	if (error || !data) {
		console.log("Error when retrieving child data");
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			i18n.tr.childData.alertMessageRetrieving,
			true,
			true,
		);
		return [];
	}
	if (displayChildImages) {
		for (const child of data) {
			const { data, error } = await getChildImage({
				path: { child_id: child.id },
			});
			if (!error && data) {
				child.image = URL.createObjectURL(data as Blob);
			}
		}
	}
	return data;
}

const promise = $state(setup());
</script>

{#await promise}
    <Spinner/>
    <p>{i18n.tr.userData.loadingMessage}</p>
{:then children}
    <div class="m-2 mx-auto w-full pb-4 md:rounded-t-lg">

        <Heading tag="h1" class="m-2 mb-2" color="text-gray-700 dark:text-gray-400">
            {i18n.tr.childData.overviewLabel}
        </Heading>

        <div class="cols-1 grid w-full gap-y-2">
            <p class="w-auto p-2 text-lg text-gray-700 dark:text-gray-400">
                {i18n.tr.childData.overviewSummary}
            </p>
            <GalleryDisplay bind:searchTerm={searchTerm}>
                {#each children as child}
                    {#if child.name && child.name.toLowerCase().includes(searchTerm.toLowerCase())}
                        <ChildCardDisplay {child}/>
                    {/if}
                {/each}
                <CardDisplay title={i18n.tr.childData.newChildHeading}
                             text={i18n.tr.childData.newChildHeadingLong}
                             color="#7c9e9d"
                             onclick={() => {currentChild.id = null; goto("/userLand/children/registration");}} />
            </GalleryDisplay>
        </div>
    </div>
{:catch error}
    {alertStore.showAlert(i18n.tr.childData.alertMessageTitle, error.message, true, true)}
{/await}
