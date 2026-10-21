<svelte:options runes={true} />
<script lang="ts">
import { Tooltip } from "flowbite-svelte";
let {
	tooltip = null,
	children,
}: {
	tooltip?: string | null;
	children?: any;
} = $props();
</script>

<div class="flex cursor-pointer items-center gap-4">
	{@render children?.()}
	{#if tooltip}
		<Tooltip arrow={false}>{tooltip}</Tooltip>
	{/if}
</div>
