<script lang="ts">
	import { Button, Dropdown, DropdownItem, Gallery, Heading, Search } from 'flowbite-svelte';
	import { ChevronDownOutline } from 'flowbite-svelte-icons';
	import { tick } from 'svelte';

	export let data;
	export let header: string | null = null;
	export let itemComponent;
	export let withSearch = true;
	export let componentProps;

	export let searchData = [
		{
			label: 'Alle',
			placeholder: 'Durchsuchen',
			filterFunction: (data: any[], searchTerm: string): any[] => {
				if (searchTerm === '') {
					return data;
				} else {
					return data.filter((item) =>
						Object.values(item).some((element) => {
							return element.toLowerCase().includes(searchTerm.toLowerCase());
						})
					);
				}
			}
		}
	];

	let searchCategory: string = searchData[0].label;
	let searchPlaceHolder: string = searchData[0].placeholder;
	let filterData = searchData[0].filterFunction;
	let dropdownOpen: boolean = false;

	// dynamic statements
	let searchTerm = '';
	$: filteredItems = withSearch === true ? filterData(data, searchTerm) : data;

	// Create a new array of componentProps that matches the filtered data
	$: filteredComponentProps = filteredItems.map((item) => {
		const index = data.indexOf(item);
		return componentProps[index];
	});
</script>

<div class="mx-auto p-4">
	{#if header !== null}
		<Heading
			tag="h1"
			class="m-2 mt-4 flex w-full gap-2 p-2 tracking-tight "
			customSize="text-2xl"
			color="text-gray-800 dark:text-white"
		>
			{header}
		</Heading>
	{/if}

	{#if withSearch}
		<form class="m-2 flex w-full rounded p-4">
			{#if searchData.length > 1}
				<!-- after example: https://flowbite-svelte.com/docs/forms/search-input#Search_with_dropdown -->
				<div class="relative">
					<Button
						class="border-primary-700 h-full whitespace-nowrap rounded-e-none border border-e-0"
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
					size="md"
					class="rounded py-2.5"
					placeholder={searchPlaceHolder}
					bind:value={searchTerm}
				/>
			{/if}
		</form>
	{/if}

	<Gallery
		class="grid w-full grid-cols-1 justify-center gap-8 p-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
	>
		{#each filteredItems as item, index}
			<svelte:component
				this={itemComponent}
				data={item}
				styleProps={filteredComponentProps[index]}
			/>
		{/each}
	</Gallery>
</div>
