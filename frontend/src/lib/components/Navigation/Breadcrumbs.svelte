<svelte:options runes={true} />
<script lang="ts">
import { Breadcrumb, BreadcrumbItem } from "flowbite-svelte";
import { PlayOutline } from "flowbite-svelte-icons";
let { data, stayExpanded = false }: { data: any[]; stayExpanded?: boolean } =
	$props();
</script>

<Breadcrumb
	olClass="inline-flex items-center space-x-1 rtl:space-x-reverse md:space-x-3 rtl:space-x-reverse  flex-wrap "
	navClass="m-4"
	solidClass="rounded-tl rounded-tr flex px-5 py-3 text-gray-700 border border-gray-200 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 "
	solid
>
	{#each data as item}
		<BreadcrumbItem
			href={item.href}
			linkClass="ms-1 text-sm md:text-base font-medium text-gray-500 hover:text-gray-700 md:ms-2 dark:text-gray-400  hover:text-white dark:hover:text-white"
		>
		<div class="flex items-center justify-center">
			{#if item.href}
				{#if item.symbol !== undefined && item.symbol !== null}
				<item.symbol size = "xl" />
				{:else}
				<PlayOutline size = "xl" />
				{/if}
				<span class="{stayExpanded ? '' : 'hidden md:'}inline">{item.label} </span>
			{:else}
				<button
					class="text-sm md:text-base ms-1 font-medium text-gray-500 hover:text-gray-700 md:ms-2 dark:text-gray-400  dark:hover:text-white"
					onclick={item.onclick}
					>
					<div class="flex items-center justify-center">
						{#if item.symbol !== undefined && item.symbol !== null}
						<item.symbol size = "xl" />
						{:else}
						<PlayOutline size = "xl" />
						{/if}
						<span class="{stayExpanded ? '' : 'hidden md:'}inline">{item.label}</span>
					</div>
				</button>
			{/if}
			</div>
		</BreadcrumbItem>
	{/each}
</Breadcrumb>
