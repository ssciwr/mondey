<script lang="ts">
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { type ChildData, children } from "$lib/stores/childrenStore";

import { createStyle, init } from "$lib/components/ChildrenGallery";
import { Heading } from "flowbite-svelte";
import { onDestroy, onMount } from "svelte";

let data: ChildData[] = [];

export let breadcrumbdata: any[] | null = null;

function searchName(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		const res = data.filter((item) => {
			return item.header.toLowerCase().includes(key.toLowerCase());
		});
		return res;
	}
}

function searchRemarks(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		const res = data.filter((item) => {
			return item.summary.toLowerCase().includes(key.toLowerCase());
		});
		return res;
	}
}

function searchAll(data: any[], key: string) {
	return [...new Set([...searchName(data, key), ...searchRemarks(data, key)])];
}

const searchData = [
	{
		label: "Alle",
		placeholder: "Alle Kategorien durchsuchen",
		filterFunction: searchAll,
	},
	{
		label: "Name",
		placeholder: "Kinder nach Namen durchsuchen",
		filterFunction: searchName,
	},
	{
		label: "Bemerkung",
		placeholder: "Bemerkungen zu Kindern durchsuchen",
		filterFunction: searchRemarks,
	},
];

// this fetches dummy child data for the dummy user whenever the component is mounted into the dom
// it is conceptualized as emulating an API call that would normally fetch this from the server.
onMount(async () => {
	data = await init();
});
onDestroy(async () => {
	children.save();
});
</script>

<div class="container m-2 mx-auto w-full pb-4 md:rounded-t-lg">
	{#if breadcrumbdata}
		<Breadcrumbs data={breadcrumbdata} />
	{/if}

	<Heading tag="h1" class="m-2 mb-2 p-4 " color="text-gray-700 dark:text-gray-400"
		>Übersicht</Heading
	>

	<div class="cols-1 grid w-full gap-y-8 p-2">
		<p class="w-auto p-2 text-lg text-gray-700 dark:text-gray-400">
			Wählen sie ein Kind zur Beobachtung aus oder legen melden sie ein neues Kind an.
		</p>
		<GalleryDisplay
			{data}
			itemComponent={CardDisplay}
			componentProps={createStyle(data)}
			{searchData}
		/>
	</div>
</div>
