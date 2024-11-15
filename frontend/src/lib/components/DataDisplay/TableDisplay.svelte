<svelte:options runes={true} />
<script lang="ts">
import { TableBody, TableBodyRow, TableSearch } from "flowbite-svelte";

import TableCell from "$lib/components/DataDisplay/TableElements/TableCell.svelte";
import TableHeader from "$lib/components/DataDisplay/TableElements/TableHeader.svelte";

function filterItemsDefault(
	data: any,
	searchTerm: string,
	searchableColumns: string[],
) {
	// toString here for generality
	return data.filter((item: any) =>
		searchableColumns.some((column) =>
			item[column]?.toString().includes(searchTerm),
		),
	);
}

function makePlaceholderTextDefault(data: any, searchableColumns: string[]) {
	const numCols = Object.keys(data[0]).length;
	let placeholderText = "Filter ";

	if (searchableColumns.length === 1) {
		placeholderText = placeholderText + searchableColumns[0];
	} else if (
		searchableColumns.length > 1 &&
		searchableColumns.length <= numCols / 2
	) {
		placeholderText = `Filter any of ${searchableColumns.join(", ")}`;
	} else if (
		searchableColumns.length > numCols / 2 &&
		searchableColumns.length < numCols
	) {
		const difference = Object.keys(data[0]).filter(
			(key) => !searchableColumns.includes(key),
		);
		placeholderText = `Filter all columns except ${difference.join(", ")}`;
	} else if (searchableColumns.length === numCols) {
		placeholderText = "Filter all columns";
	} else {
		placeholderText = "Filter disabled";
	}

	return placeholderText;
}

let {
	data = [],
	celllinks = [],
	caption = "",
	statusColumns = [],
	searchableColumns = [],
	statusIndicator = {},
	headerlinks = [],
	filterItems = filterItemsDefault,
	makePlaceholderText = makePlaceholderTextDefault,
}: {
	data: any[];
	celllinks: string[][];
	caption: string;
	statusColumns: string[];
	searchableColumns: string[];
	statusIndicator: Record<string, string>;
	headerlinks: string[];
	filterItems: (
		data: any,
		searchTerm: string,
		searchableColumns: string[],
	) => any[];
	makePlaceholderText: (data: any, searchableColumns: string[]) => string;
} = $props();

// make the placeholdertext for the searchbar dynamic
const placeholderText = makePlaceholderText(data, searchableColumns);
let searchTerm = $state("");

// reactive statements
let filteredItems = $derived(filterItems(data, searchTerm, searchableColumns));
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
						value={pair[1] as string}
						{statusIndicator}
						{statusColumns}
						href={celllinks?.[i]?.[j] || ''}
					/>
				{/each}
			</TableBodyRow>
		{/each}
	</TableBody>
</TableSearch>
