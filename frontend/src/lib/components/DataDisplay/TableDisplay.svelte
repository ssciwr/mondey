<svelte:options runes={true} />
<script lang="ts">
import { TableBody, TableBodyRow, TableSearch } from "flowbite-svelte";

import TableCell from "$lib/components/DataDisplay/TableElements/TableCell.svelte";
import TableHeader from "$lib/components/DataDisplay/TableElements/TableHeader.svelte";

import {
	filterItemsDefault,
	makePlaceholderTextDefault,
} from "$lib/components/DataDisplay/TableDisplayHelpers";

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
