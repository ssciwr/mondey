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

/* From stackoverflow: https://stackoverflow.com/a/41491220 | SudoPlz | CC BY-SA 4.0
 * Ensures that we use a high contrast color given we are allowing unlimited colors to be selected by the user
 * */
function isDark(bgColor: string): boolean {
	if (!bgColor) return false; // either a kid with an image but no color(so bg is white, not dark), or "Add new kid"
	let color = bgColor.charAt(0) === "#" ? bgColor.substring(1, 7) : bgColor;
	let r = Number.parseInt(color.substring(0, 2), 16); // hexToR
	let g = Number.parseInt(color.substring(2, 4), 16); // hexToG
	let b = Number.parseInt(color.substring(4, 6), 16); // hexToB
	return r * 0.299 + g * 0.587 + b * 0.114 <= 186;
}

function createStyle(data: CardElement[]): CardStyle[] {
	return data.map((item) => {
		const contextualTextColor = isDark(item.color as string)
			? "text-white"
			: "text-black";
		return {
			card:
				item.header === i18n.tr.childData.newChildHeading
					? {
							class:
								"bg-primary dark:bg-primary child-card hover:cursor-pointer m-2 max-w-prose hover:bg-additional-color-800 dark:hover:bg-additional-color-700 ",
							horizontal: false,
						}
					: {
							class:
								"child-card hover:cursor-pointer m-2 max-w-prose text-gray-700 hover:text-white dark:text-white hover:dark:text-gray-400 hover:bg-primary-800 dark:hover:bg-primary-700",
							style: item.color
								? `background-color: ${item.color};`
								: "background-color: white", // default to white for image ones, even on hover.
							horizontal: false,
						},
			header:
				item.header === i18n.tr.childData.newChildHeading
					? {
							class:
								"mb-2 text-2xl font-bold tracking-tight text-white dark:text-white",
						}
					: {
							class: `mb-2 text-2xl font-bold tracking-tight ${contextualTextColor}`,
						},
			summary:
				item.header === i18n.tr.childData.newChildHeading
					? {
							class:
								"mb-3 flex font-normal leading-tight text-white dark:text-white",
						}
					: {
							class: `opacity-60 ${contextualTextColor}`,
						},
			button: null,
			progress: null,
			auxilliary: null,
		};
	});
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
					summary: `${child.birth_month}/${child.birth_year}`,
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

	<div class="m-2 mx-auto w-full pb-4 md:rounded-t-lg">

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
