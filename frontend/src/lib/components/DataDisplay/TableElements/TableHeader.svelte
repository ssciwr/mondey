<script lang="ts">
import { TableHead, TableHeadCell } from "flowbite-svelte";

export let caption: string;
export let columns: string[];
export let links: string[];
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
