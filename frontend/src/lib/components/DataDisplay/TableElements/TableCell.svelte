<svelte:options runes={true} />
<script lang="ts">
import { TableBodyCell } from "flowbite-svelte";

let {
	value,
	statusIndicator,
	statusColumns,
	key,
	href = "",
}: {
	value: string;
	statusIndicator: Record<string, string>;
	statusColumns: string[];
	key: string;
	href?: string;
} = $props();
</script>

{#if statusColumns.includes(key)}
	<TableBodyCell class={'hover:opacity-80 ' + statusIndicator[value]}>
		{#if href !== ''}
			<a {href}>{value}</a>
		{:else}
			{value}
		{/if}
	</TableBodyCell>
{:else}
	<TableBodyCell class="hover:opacity-80">
		{#if href !== ''}
			<a {href}>{value}</a>
		{:else}
			{value}
		{/if}
	</TableBodyCell>
{/if}
