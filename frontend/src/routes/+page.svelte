<svelte:options runes={true} />

<script lang="ts">
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageAccordion from "$lib/components/FrontPageAccordion.svelte";
import FrontPageBookmarks from "$lib/components/FrontPageBookmarks.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import { i18n } from "$lib/i18n.svelte";
</script>

<FrontPageCard/>

<FrontPageAbout/>

<div class="flex mt-7 flex-col text-center justify-center items-center space-y-6">
    <h1 class="text-2xl dark:text-white justify-center text-center text-balance max-w-prose font-bold text-gray-700">{i18n.tr.frontpageBookmarks.title}</h1>
    <FrontPageBookmarks />
</div>

<FrontPageAccordion/>
