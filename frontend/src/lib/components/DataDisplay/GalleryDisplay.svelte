<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Checkbox, Radio, Search } from "flowbite-svelte";
import { type Snippet } from "svelte";

let {
	searchTerm = $bindable(),
	showIncompleteOnly = $bindable(null),
	children,
}: {
	searchTerm?: string;
	showIncompleteOnly?: null | boolean;
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
        <div class="my-2 flex flex-row gap-3">
            <label class="flex items-center border border-gray-300 rounded-lg px-3 py-2 cursor-pointer">
                <Radio
                    bind:group={showIncompleteOnly}
                    value={true}
                    class="sr-only"
                    custom={true}
                />
                <div class="w-4 h-4 rounded-full border-2 mr-2 flex items-center justify-center {showIncompleteOnly === true ? 'border-milestone-500' : 'border-gray-300'}">
                    <div class="w-2 h-2 rounded-full {showIncompleteOnly === true ? 'bg-milestone-500' : 'bg-transparent'}"></div>
                </div>
                <span>{i18n.tr.milestone.showIncompleteOnly}</span>
            </label>
            <label class="flex items-center border border-gray-300 rounded-lg px-3 py-2 cursor-pointer">
                <Radio
                    bind:group={showIncompleteOnly}
                    value={false}
                    class="sr-only"
                    custom={true}
                />
                <div class="w-4 h-4 rounded-full border-2 mr-2 flex items-center justify-center {showIncompleteOnly === false ? 'border-milestone-500' : 'border-gray-300'}">
                    <div class="w-2 h-2 rounded-full {showIncompleteOnly === false ? 'bg-milestone-500' : 'bg-transparent'}"></div>
                </div>
                <span>{i18n.tr.milestone.showAll}</span>
            </label>
        </div>
    {/if}
</form>
<div class="grid w-full grid-cols-1 justify-center p-2 gap-8 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
    {@render children?.()}
</div>
