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

<div class="functional-icon-container">
	{@render children?.()}
	{#if tooltip}
		<Tooltip arrow={false}>{tooltip}</Tooltip>
	{/if}
</div>

<style>
	:global(.functional-icon-container) {
		@apply flex cursor-pointer items-center space-x-4 rtl:space-x-reverse;
	}

	:global(.apply-icon-style) {
		@apply rounded-lg p-2 text-xl text-gray-500;
	}

	:global(.apply-icon-style:hover) {
		@apply text-primary-800;
	}

	:global(.apply-icon-style.group-hover) {
		@apply text-primary-800;
	}

	:global(.apply-icon-style.dark) {
		@apply text-gray-400;
	}

	:global(.apply-icon-style.dark:hover) {
		@apply text-primary-500;
	}

	:global(.apply-icon-style.dark.group-hover) {
		@apply text-primary-500;
	}
</style>
