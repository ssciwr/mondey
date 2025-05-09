<svelte:options runes={true} />
<script lang="ts">
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import {
	Button,
	Dropdown,
	DropdownItem,
	Heading,
	Search,
} from "flowbite-svelte";
import { ChevronDownOutline } from "flowbite-svelte-icons";
import { type Component, tick } from "svelte";

let {
	data = [],
	header = null,
	itemComponent = CardDisplay,
	withSearch = true,
	componentProps = {},
	searchData = [
		{
			label: "Alle",
			placeholder: "Durchsuchen",
			filterFunction: (data: any[], searchTerm: string): any[] => {
				return data;
			},
		},
	],
}: {
	data?: any[];
	header?: string | null;
	itemComponent?: Component<any, Record<string, any>, "">;
	withSearch?: boolean;
	componentProps?: any;
	searchData?: {
		label: string;
		placeholder: string;
		filterFunction: (data: any[], searchTerm: string) => any[];
	}[];
} = $props();

let filterData = searchData[0].filterFunction;
let searchCategory: string = $state(searchData[0].label);
let searchPlaceHolder: string = $state(searchData[0].placeholder);
let dropdownOpen = $state(false);
let searchTerm = $state("");
let filteredItems = $derived(
	withSearch === true ? filterData(data, searchTerm) : data,
);

// Create a new array of componentProps that matches the filtered data
let filteredComponentProps = $derived(
	filteredItems.map((item) => {
		const index = data.indexOf(item);
		return componentProps[index];
	}),
);
</script>

<div class="mx-auto p-4 w-full">
	{#if header !== null}
		<Heading
			tag="h1"
			class="m-2 mt-4 flex w-full gap-2 p-2 tracking-tight whitespace-nowrap"
			customSize="text-2xl"
			color="text-gray-800 dark:text-white"
		>
			{header}
		</Heading>
	{/if}

	{#if withSearch}
		<form class="m-2 w-full rounded p-4 {searchData.length > 1 ? 'flex' : ''}">
		{#if searchData.length > 1}
				<!-- after example: https://flowbite-svelte.com/docs/forms/search-input#Search_with_dropdown -->
				<div class="relative">
					<Button
						class="h-full whitespace-nowrap rounded-e-none border border-e-0 border-primary-700"
					>
						{searchCategory}
						<ChevronDownOutline class="ms-2.5 h-2.5 w-2.5" />
					</Button>
					<Dropdown classContainer="flex w-auto" bind:open={dropdownOpen}>
						{#each searchData as { label, placeholder, filterFunction }}
							<DropdownItem
								on:click={async () => {
									searchCategory = label;
									searchPlaceHolder = placeholder;
									filterData = filterFunction;
									dropdownOpen = false;
									await tick();
								}}
								class={searchCategory === label ? 'underline' : ''}
							>
								{label}
							</DropdownItem>
						{/each}
					</Dropdown>
				</div>
				<Search
					class="rounded-e rounded-s-none py-2.5"
					size="md"
					placeholder={searchPlaceHolder}
					bind:value={searchTerm}
				/>
			{:else}
				<Search
					size="lg"
					class="rounded py-2.5 min-w-full"
					placeholder={searchPlaceHolder}
					bind:value={searchTerm}
				/>
			{/if}
		</form>
	{/if}

	<div
		class="grid w-full grid-cols-1 justify-center gap-8 p-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3"
	>
		{#each filteredItems as item, index}
			<svelte:component
				this={itemComponent}
				data={item}
				styleProps={filteredComponentProps[index]}
			/>
		{/each}
	</div>
</div>
