<svelte:options runes={true} />

<script lang="ts">
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageAccordion from "$lib/components/FrontPageAccordion.svelte";
import FrontPageBookmarks from "$lib/components/FrontPageBookmarks.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Modal } from "flowbite-svelte";
import { onMount } from "svelte";

let showDisclaimerModal = $state(false);

onMount(() => {
    showDisclaimerModal = true;
});
</script>

<FrontPageCard/>

<FrontPageAbout/>

<div class="flex mt-7 flex-col text-center justify-center items-center space-y-6">
    <h1 class="text-2xl dark:text-white justify-center text-center text-balance max-w-prose font-bold text-gray-700">{i18n.tr.frontpageBookmarks.title}</h1>
    <FrontPageBookmarks />
</div>

<FrontPageAccordion/>

<Modal bind:open={showDisclaimerModal} autoclose>
    <div class="p-4 text-center">
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {i18n.tr.frontpage.disclaimerPopup}
        </h3>
    </div>
</Modal>
