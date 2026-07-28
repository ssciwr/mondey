<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Heading, P } from "flowbite-svelte";
</script>

<svelte:head>
    <title>{i18n.tr.privacy.pageTitle} - MONDEY</title>
</svelte:head>

<Heading
        tag="h3"
        class="divide-y divide-gray-200 text-gray-900 dark:divide-gray-700 dark:text-white pt-12 pb-2 pl-12"
>{i18n.tr.privacy.pageTitle}</Heading
>

<P
        class="divide-y divide-gray-200 whitespace-pre-line text-gray-500 dark:divide-gray-700 dark:text-white px-12 pb-12"
>{i18n.tr.privacy.text}</P
>
