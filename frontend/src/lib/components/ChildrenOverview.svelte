<svelte:options runes={true} />

<script lang="ts">
import {
    createChild,
    getChildImage,
    getChildren,
} from "$lib/client/services.gen";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore";
import { activeTabChildren } from "$lib/stores/componentStore";
import { Heading } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";

async function setup(): Promise<any> {
	data = [
		{
			header: "Neu",
			summary: "Ein neues Kind anmelden",
			events: {
				onclick: async () => {
					const new_child = await createChild({
						body: {
							name: "",
							birth_year: 0,
							birth_month: 0,
							remark: "",
						},
					});

					if (new_child.error) {
						showAlert = true;
						alertMessage = new_child.error.detail;
					} else {
						currentChild.set(new_child.data.id);

						activeTabChildren.update((value: string) => {
							return "childrenRegistration";
						});
					}
				},
			},
			image: null,
		},
	];

	const children = await getChildren();

	if (children.error) {
		console.log("Error when retrieving child data");
		showAlert = true;
		alertMessage = children.error.detail;
	} else {
		for (const child of children.data) {
			data.push({
				header: child.name,
				summary: child.remark,
				image: null,
				events: {
					onclick: () => {
						currentChild.set(child.id);
						activeTabChildren.update((value: string) => {
							return "childrenRegistration";
						});
					},
				},
			});
			if (child.has_image) {
				const childimage = await getChildImage({
					path: {
						child_id: child.id,
					},
				});
				if (childimage.error) {
					console.log("Error when retrieving child image");
					showAlert = true;
					alertMessage = childimage.error.detail;
				} else {
					const reader = new FileReader();
					// FIXME: This is a hack to get the image into the data array. It should go into a function, but this interfers with the async stuff and causes the image not to show up as it should
					reader.onloadend = function(e) {
						const index = data.findIndex(item => item.header === child.name); 
						data[index].image = e.target.result;
					};
					reader.readAsDataURL(childimage.data);
				}
			}
		}
	}
	return data;
}

function createStyle(data: any[]) {
	return data.map((item) => ({
		card:
			item.header === "Neu"
				? {
						class:
							"hover:cursor-pointer m-2 max-w-prose bg-primary-700 dark:bg-primary-600 hover:bg-primary-800 dark:hover:bg-primary-700",
						horizontal: false,
					}
				: { horizontal: false },
		header:
			item.header == "Neu"
				? {
						class:
							"mb-2 text-2xl font-bold tracking-tight text-white dark:text-white",
					}
				: null,
		summary:
			item.header == "Neu"
				? {
						class:
							"mb-3 flex font-normal leading-tight text-white dark:text-white",
					}
				: null,
		button: null,
	}));
}

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

let { breadcrumbdata = null }: { breadcrumbdata: any[] | null } = $props();
let showAlert = $state(false);
let alertMessage = "Error";
let data: any[]  = $state([]);

const promise = $state(setup());
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
</script>

{#await promise}
	<p>{"Waiting for server response"}</p>
{:then data}
	<div class="container m-2 mx-auto w-full pb-4 md:rounded-t-lg">
		{#if breadcrumbdata}
			<Breadcrumbs data={breadcrumbdata} />
		{/if}

		<Heading
			tag="h1"
			class="m-2 mb-2 p-4 "
			color="text-gray-700 dark:text-gray-400">Übersicht</Heading
		>

		<div class="cols-1 grid w-full gap-y-8 p-2">
			<p class="w-auto p-2 text-lg text-gray-700 dark:text-gray-400">
				Wählen sie ein Kind zur Beobachtung aus oder legen melden sie
				ein neues Kind an.
			</p>
			<GalleryDisplay
				{data}
				itemComponent={CardDisplay}
				componentProps={createStyle(data)}
				{searchData}
			/>
		</div>
	</div>
{:catch error}
	<AlertMessage
		title={"Error in server request"}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
