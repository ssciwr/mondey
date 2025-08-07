<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Checkbox, Search } from "flowbite-svelte";
import { type Snippet } from "svelte";

let {
	searchTerm = $bindable(),
	showIncompleteOnly = $bindable(null),
	showIncompleteTranslation,
	children,
}: {
	searchTerm?: string;
	showIncompleteOnly?: null | boolean;
	showIncompleteTranslation?: string;
	children?: Snippet;
} = $props();
</script>

<form class="py-4 w-full rounded p-2">
    {#if searchTerm !== undefined}
        <Search
                bind:value={searchTerm}
                class="rounded py-2.5 min-w-full"
                placeholder={i18n.tr.search.namePlaceholder}
                size="lg"
        />
    {/if}
    {#if showIncompleteOnly !== null}
        <Checkbox bind:checked={showIncompleteOnly} class="my-2">
            {showIncompleteTranslation || i18n.tr.search.showIncompleteOnly}
        </Checkbox>
    {/if}
</form>
<div class="grid w-full grid-cols-1 justify-center p-2 gap-8 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
    {@render children?.()}
</div>
