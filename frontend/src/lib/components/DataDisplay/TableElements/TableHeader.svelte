<svelte:options runes={true} />
<script lang="ts">
import { TableHead, TableHeadCell } from "flowbite-svelte";

let {
	caption = undefined,
	columns = [],
	links = [],
}: {
	caption?: string;
	columns?: string[];
	links?: string[];
} = $props();
</script>

<caption class="mb-4 font-normal leading-tight text-gray-700 dark:text-gray-400">
	{caption}
</caption>
<TableHead>
	{#each columns as key, i}
		<TableHeadCell>
			{#if links[i]}
				<a href={links[i]}>{key}</a>
			{:else}
				{key}
			{/if}
		</TableHeadCell>
	{/each}
</TableHead>
