<script lang="ts">
import { TableBodyCell } from "flowbite-svelte";

export let value;
export let statusIndicator;
export let statusColumns;
export let key;
export let href = "";
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
