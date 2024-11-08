<svelte:options runes={true} />

<script lang="ts">
import { getChildImage, getChildren } from "$lib/client/services.gen";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { currentChild } from "$lib/stores/childrenStore";
import { activeTabChildren } from "$lib/stores/componentStore";
import { Heading } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

async function setup(): Promise<any> {
	const children = await getChildren();

	if (children.error) {
		console.log("Error when retrieving child data");
		showAlert = true;
		alertMessage =
			$_("childData.alertMessageRetrieving") + children.error.detail;
	} else {
		const childrenData = await Promise.all(
			children.data.map(async (child) => {
				let image = null;
				if (child.has_image) {
					const childImageResponse = await getChildImage({
						path: { child_id: child.id },
					});
					if (childImageResponse.error) {
						console.log("Error when retrieving child image");
						showAlert = true;
						alertMessage =
							$_("childData.alertMessageImage") +
							childImageResponse.error.detail;
					} else {
						const reader = new FileReader();
						reader.readAsDataURL(childImageResponse.data);
						image = await new Promise((resolve) => {
							reader.onloadend = () => resolve(reader.result as string);
						});
					}
				}
				return {
					header: child.name,
					image,
					events: {
						onclick: () => {
							currentChild.set(child.id);
							activeTabChildren.set("childrenRegistration");
						},
					},
				};
			}),
		);

		// add the 'new child' card as the first element
		data = [
			{
				header: $_("childData.newChildHeading"),
				summary: $_("childData.newChildHeadingLong"),
				events: {
					onclick: async () => {
						currentChild.set(null);
						activeTabChildren.set("childrenDataInput");
					},
				},
				image: null,
			},
			...childrenData,
		];
	}
	return data;
}

function createStyle(data: any[]) {
	return data.map((item) => ({
		card:
			item.header === $_("childData.newChildHeading")
				? {
						class:
							"hover:cursor-pointer m-2 max-w-prose bg-primary-700 dark:bg-primary-600 hover:bg-primary-800 dark:hover:bg-primary-700",
						horizontal: false,
					}
				: { horizontal: false },
		header:
			item.header == $_("childData.newChildHeading")
				? {
						class:
							"mb-2 text-2xl font-bold tracking-tight text-white dark:text-white",
					}
				: null,
		summary:
			item.header == $_("childData.newChildHeading")
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

let showAlert = $state(false);
let alertMessage = $_("childData.alertMessageError");
let data: any[] = $state([]);

const promise = $state(setup());
const searchData = [
	{
		label: $_("childData.searchNameLabel"),
		placeholder: $_("childData.searchNamePlaceholder"),
		filterFunction: searchName,
	},
];
</script>

{#await promise}
	<p>{"Waiting for server response"}</p>
{:then data}
	<div class="container m-2 mx-auto w-full pb-4 md:rounded-t-lg">

		<Heading
			tag="h1"
			class="m-2 mb-2 p-4 "
			color="text-gray-700 dark:text-gray-400">{$_("childData.overviewLabel")}</Heading
		>

		<div class="cols-1 grid w-full gap-y-8 p-2">
			<p class="w-auto p-2 text-lg text-gray-700 dark:text-gray-400">
				{$_("childData.overviewSummary")}
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
