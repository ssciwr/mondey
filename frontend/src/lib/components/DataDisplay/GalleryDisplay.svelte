<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Checkbox, Radio, Search } from "flowbite-svelte";
import { type Snippet } from "svelte";

let {
	searchTerm = $bindable(),
	showIncompleteOnly = $bindable(null),
	useRadioButtons = false,
	children,
}: {
	searchTerm?: string;
	showIncompleteOnly?: null | boolean;
	useRadioButtons?: boolean;
	children?: Snippet;
} = $props();

// For radio button mode
let filterOption = $state(showIncompleteOnly ? "incomplete" : "complete");

$effect(() => {
	if (useRadioButtons && showIncompleteOnly !== null) {
		showIncompleteOnly = filterOption === "incomplete";
	}
});
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
        {#if useRadioButtons}
            <div class="my-2 flex flex-row gap-3">
                <div class="border border-gray-300 rounded-lg px-3 py-2 cursor-pointer" onclick={() => filterOption = "incomplete"}>
                    <div class="flex items-center">
                        <div class={`w-4 h-4 rounded-full border-2 mr-2 flex items-center justify-center ${filterOption === "incomplete" ? "border-milestone-500 bg-milestone-500" : "border-gray-300"}`}>
                            {#if filterOption === "incomplete"}
                                <div class="w-2 h-2 rounded-full bg-white"></div>
                            {/if}
                        </div>
                        <span>{i18n.tr.milestone.nochBearbeiten}</span>
                    </div>
                </div>
                <div class="border border-gray-300 rounded-lg px-3 py-2 cursor-pointer" onclick={() => filterOption = "complete"}>
                    <div class="flex items-center">
                        <div class={`w-4 h-4 rounded-full border-2 mr-2 flex items-center justify-center ${filterOption === "complete" ? "border-milestone-500 bg-milestone-500" : "border-gray-300"}`}>
                            {#if filterOption === "complete"}
                                <div class="w-2 h-2 rounded-full bg-white"></div>
                            {/if}
                        </div>
                        <span>{i18n.tr.milestone.schonBearbeitet}</span>
                    </div>
                </div>
            </div>
        {:else}
            <Checkbox bind:checked={showIncompleteOnly} class="my-2">
                {i18n.tr.search.showIncompleteOnly}
            </Checkbox>
        {/if}
    {/if}
</form>
<div class="grid w-full grid-cols-1 justify-center p-2 gap-8 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
    {@render children?.()}
</div>
