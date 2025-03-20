<!--
This component will abstract and reduce the boilderplate for the await promise --> then data ---> catch error process.

It will accept the promise, the error messages for await failure, and then the component (as a child) to render when data loads.

It will show a spinner automatically.

The motivation is that this slightly reduces LoC while being fairly clear and letting us handle all await errors through
the same abstracted component.

-->

<script>
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { i18n } from "$lib/i18n.svelte.js";
import { alertStore } from "$lib/stores/alertStore.svelte.js";
import { Heading, Spinner } from "flowbite-svelte";

let {
	promise,
	awaitErrorTitle = "Error",
	awaitErrorMessage = "An error occurred while loading data.",
} = $props();
</script>

{#await promise}
    <div class="flex flex-col items-center justify-center space-y-2 p-4">
        <Spinner />
        <p class="text-center text-gray-700 dark:text-gray-400">
            <slot name="loading-message">Loading...</slot>
        </p>
    </div>
{:then data}
    <slot {data}>{data}</slot>
{:catch error}
    {alertStore.showAlert(awaitErrorTitle, awaitErrorMessage || error.message, true, true)}
{/await}
