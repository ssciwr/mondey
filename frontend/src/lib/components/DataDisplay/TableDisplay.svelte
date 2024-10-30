<script context="module">
export function filterItems(data, searchTerm, searchableColumns) {
	// toString here for generality
	return data.filter((item) =>
		searchableColumns.some((column) =>
			item[column]?.toString().includes(searchTerm),
		),
	);
}

export function makePlaceholderText(data, searchableColumns) {
	const numCols = Object.keys(data[0]).length;
	let placeholderText = "Filter ";

	if (searchableColumns.length === 1) {
		placeholderText = placeholderText + searchableColumns[0];
	} else if (
		searchableColumns.length > 1 &&
		searchableColumns.length <= numCols / 2
	) {
		placeholderText = "Filter " + `any of ${searchableColumns.join(", ")}`;
	} else if (
		searchableColumns.length > numCols / 2 &&
		searchableColumns.length < numCols
	) {
		const difference = Object.keys(data[0]).filter(
			(key) => !searchableColumns.includes(key),
		);
		placeholderText = "Filter all columns except " + `${difference.join(", ")}`;
	} else if (searchableColumns.length === numCols) {
		placeholderText = "Filter all columns";
	} else {
		placeholderText = "Filter disabled";
	}

	return placeholderText;
}
</script>

<script lang="ts">
	import { TableBody, TableBodyRow, TableSearch } from 'flowbite-svelte';

	import TableCell from '$lib/components/DataDisplay/TableElements/TableCell.svelte';
	import TableHeader from '$lib/components/DataDisplay/TableElements/TableHeader.svelte';

	// exported variables
	export let data: object[] = [];
	export let celllinks: string[][] = []; // separate datastructure because it is specific to the point in the fronted where it is used but is static once defined.
	export let caption = '';
	export let statusColumns: string[] = [];
	export let searchableColumns: string[] = [];
	export let statusIndicator;
	export let headerlinks: string[] = [];

	// make the placeholdertext for the searchbar dynamic
	const placeholderText = makePlaceholderText(data, searchableColumns);
	let searchTerm = '';

	// reactive statements
	$: filteredItems = filterItems(data, searchTerm, searchableColumns);
</script>

<TableSearch
	placeholder={placeholderText}
	bind:inputValue={searchTerm}
	hoverable={true}
	striped={true}
>
	<TableHeader {caption} columns={Object.keys(data[0])} links={headerlinks} />
	<TableBody tableBodyClass="divide-y">
		{#each filteredItems as row, i}
			<TableBodyRow>
				{#each Object.entries(row) as pair, j}
					<TableCell
						key={pair[0]}
						value={pair[1]}
						{statusIndicator}
						{statusColumns}
						href={celllinks?.[i]?.[j] || ''}
					/>
				{/each}
			</TableBodyRow>
		{/each}
	</TableBody>
</TableSearch>
