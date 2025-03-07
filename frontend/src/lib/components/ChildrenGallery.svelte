<svelte:options runes={true} />

<script lang="ts">
import { getChildImage, getChildren } from "$lib/client/services.gen";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage } from "$lib/stores/componentStore";
import { type CardElement, type CardStyle } from "$lib/util";
import { Heading, Spinner } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";

function createStyle(data: CardElement[]): CardStyle[] {
	return data.map((item) => ({
		card:
			item.header === i18n.tr.childData.newChildHeading
				? {
						class:
							"hover:cursor-pointer m-2 max-w-prose bg-primary-700 dark:bg-primary-600 hover:bg-primary-800 dark:hover:bg-primary-700",
						horizontal: false,
					}
				: {
						class:
							"hover:cursor-pointer m-2 max-w-prose text-gray-700 hover:text-white dark:text-white hover:dark:text-gray-400 hover:bg-primary-800 dark:hover:bg-primary-700",
						style: item.color ? `background-color: ${item.color};` : "",
						horizontal: false,
					},
		header:
			item.header === i18n.tr.childData.newChildHeading
				? {
						class:
							"mb-2 text-2xl font-bold tracking-tight text-white dark:text-white",
					}
				: null,
		summary:
			item.header === i18n.tr.childData.newChildHeading
				? {
						class:
							"mb-3 flex font-normal leading-tight text-white dark:text-white",
					}
				: null,
		button: null,
		progress: null,
		auxilliary: null,
	}));
}

function searchName(data: CardElement[], key: string): CardElement[] {
	if (key === "") {
		return data;
	}

	const res = data.filter((item) => {
		if (item.header === null || item.header === undefined) {
			return false;
		}

		return item.header.toLowerCase().includes(key.toLowerCase());
	});
	return res;
}

async function setup(): Promise<CardElement[]> {
	const children = await getChildren();

	if (children.error) {
		console.log("Error when retrieving child data");
		showAlert = true;
		alertMessage = i18n.tr.childData.alertMessageRetrieving;
	} else {
		const childrenData = await Promise.all(
			(children.data || []).map(async (child): Promise<CardElement> => {
				let image = undefined as string | undefined;
				const childImageResponse = await getChildImage({
					path: { child_id: child.id },
				});
				if (!childImageResponse.error) {
					image = URL.createObjectURL(childImageResponse.data as Blob);
				}
				return {
					header: child.name,
					image,
					summary: null,
					color: child.color,
					events: {
						onclick: async () => {
							currentChild.id = child.id;
							await currentChild.load_data();
							activePage.set("childrenRegistration");
						},
					},
				};
			}),
		);

		// add the 'new child' card as the first element
		data = [
			...childrenData,
			{
				header: i18n.tr.childData.newChildHeading,
				summary: i18n.tr.childData.newChildHeadingLong,
				events: {
					onclick: () => {
						currentChild.id = null;
						activePage.set("childrenRegistration");
					},
				},
			},
		];

		style = createStyle(data);
	}
	return data;
}

let showAlert = $state(false);
let alertMessage = $state(i18n.tr.childData.alertMessageError);
let data: CardElement[] = $state([]);
let style: CardStyle[] = $state([]);
const promise = $state(setup());
const searchData = [
	{
		label: i18n.tr.childData.searchNameLabel,
		placeholder: i18n.tr.childData.searchNamePlaceholder,
		filterFunction: searchName,
	},
];
</script>

{#await promise}
	<Spinner /> <p>{i18n.tr.userData.loadingMessage}</p>
{:then data}
	{#if showAlert}
		<AlertMessage
			title={i18n.tr.childData.alertMessageTitle}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}

	<div class="container m-2 mx-auto w-full pb-4 md:rounded-t-lg">

		<Heading
			tag="h1"
			class="m-2 mb-2 p-4 "
			color="text-gray-700 dark:text-gray-400">{i18n.tr.childData.overviewLabel}</Heading
		>

		<div class="cols-1 grid w-full gap-y-8 p-2">
			<p class="w-auto p-2 text-lg text-gray-700 dark:text-gray-400">
				{i18n.tr.childData.overviewSummary}
			</p>
			<GalleryDisplay
				{data}
				itemComponent={CardDisplay}
				componentProps={style}
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
