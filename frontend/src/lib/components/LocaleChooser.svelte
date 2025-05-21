<svelte:options runes={true} />
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Dropdown, DropdownItem } from "flowbite-svelte";
import { ChevronDownOutline, LanguageOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let { withIcon = false }: { withIcon?: boolean } = $props();

let buttonId = $state("");
onMount(() => {
	buttonId = `locale-${Math.random().toString(20)}`;
});

let dropdownOpen = $state(false);
</script>

<div class="flex m-1 p-1">

	<button
		id={buttonId}
		class="z-10 inline-flex flex-shrink-0 items-center rounded-lg bg-gray-100 px-4 py-2.5 text-center text-sm font-medium text-gray-500 hover:bg-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-700"
		type="button"
	>
		{#if withIcon}
			<LanguageOutline size="lg" />
		{/if}
		{i18n.selectedLocale}
		<ChevronDownOutline class="ms-2 h-6 w-6" />
	</button>
	<Dropdown triggeredBy={buttonId} bind:open={dropdownOpen}>
		{#each i18n.locales as locale}
			<DropdownItem
				class="flex items-center"
				on:click={preventDefault(() => {
					i18n.locale = locale;
					dropdownOpen = false;
				})}
			>
				{locale}
			</DropdownItem>
		{/each}
	</Dropdown>
</div>
