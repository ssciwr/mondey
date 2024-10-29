<script lang="ts">
import { Breadcrumb, BreadcrumbItem } from "flowbite-svelte";
export let data: any[] = [];
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
			linkClass="ms-1 text-md font-medium text-gray-700 hover:text-primary-700 md:ms-2 dark:text-gray-400 dark:hover:text-white"
		>
			{#if item.href}
				{item.label}
			{:else}
				<button
					class="text-md ms-1 font-medium text-gray-700 hover:text-primary-700 md:ms-2 dark:text-gray-400 dark:hover:text-white"
					on:click={item.onclick}
					>{item.label}
				</button>
			{/if}
		</BreadcrumbItem>
	{/each}
</Breadcrumb>
