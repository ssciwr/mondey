<svelte:options runes={true} />

<script lang="ts">
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageAccordion from "$lib/components/FrontPageAccordion.svelte";
import FrontPageBookmarks from "$lib/components/FrontPageBookmarks.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Banner } from "flowbite-svelte";
import { ExclamationCircleOutline } from "flowbite-svelte-icons";
</script>

<Banner id="default-banner" position="fixed" class="bottom-0 left-0 z-50 flex justify-between w-full p-4 border-t border-gray-200 bg-gray-50 dark:bg-gray-700 dark:border-gray-600">
    <div class="flex items-center mx-auto">
        <p class="flex items-center text-sm font-normal text-gray-500 dark:text-gray-400">
            <ExclamationCircleOutline class="me-3 w-4 h-4 text-gray-500 dark:text-gray-400" />
            <span>{i18n.tr.frontpage.disclaimerPopup}</span>
        </p>
    </div>
</Banner>

<FrontPageCard/>

<FrontPageAbout/>

<div class="flex mt-7 flex-col text-center justify-center items-center space-y-6">
    <h1 class="text-2xl dark:text-white justify-center text-center text-balance max-w-prose font-bold text-gray-700">{i18n.tr.frontpageBookmarks.title}</h1>
    <FrontPageBookmarks />
</div>

<FrontPageAccordion/>
