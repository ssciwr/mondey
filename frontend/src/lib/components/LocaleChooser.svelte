<script lang="ts">
	import { Dropdown, DropdownItem } from 'flowbite-svelte';
	import { ChevronDownOutline } from 'flowbite-svelte-icons';
	import { locale, locales } from 'svelte-i18n';
	import { languages, lang_id } from '$lib/stores/langStore';

	let dropdownOpen = false;
</script>

<div class="flex">
	<button
		id="locale-button"
		class="z-10 inline-flex flex-shrink-0 items-center rounded-lg bg-gray-100 px-4 py-2.5 text-center text-sm font-medium text-gray-500 hover:bg-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-700"
		type="button"
	>
		{$locale}
		<ChevronDownOutline class="ms-2 h-6 w-6" />
	</button>
	<Dropdown triggeredBy="#locale-button" bind:open={dropdownOpen}>
		{#each $locales as loc}
			<DropdownItem
				class="flex items-center"
				on:click={() => {
					locale.set(loc);
					lang_id.set(`${Object.keys($languages).find((key) => $languages[key] === loc)}`);
					dropdownOpen = false;
				}}
			>
				{loc}
			</DropdownItem>
		{/each}
	</Dropdown>
</div>
