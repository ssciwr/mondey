<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
} from "$lib/client";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { contentStore } from "$lib/stores/contentStore.svelte";
import {
	CheckCircleSolid,
	ExclamationCircleSolid,
	GridOutline,
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { _, locale } from "svelte-i18n";

function searchStatus(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			// button label contains info about completion status => use for search
			if (key === $_("milestone.complete")) {
			} else if (key === $_("milestone.incomplete")) {
			}
		});
	}
}

function searchDescription(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.summary.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchTitle(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.header.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchAnswer(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.answer === null
				? false
				: item.answer.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchAll(data: any[], key: string): any[] {
	return [
		...new Set([
			...searchDescription(data, key),
			...searchStatus(data, key),
			...searchTitle(data, key),
			...searchAnswer(data, key),
		]),
	];
}

async function setup(): Promise<void> {
	console.log("setup overview");
	await currentChild.load_data();
	if (
		!contentStore.milestoneGroupData.milestones ||
		contentStore.milestoneGroupData.milestones.length === 0
	) {
		console.log("Error when retrieving milestone groups");
		showAlert = true;
		alertMessage = $_("milestoneGroup.alertMessageRetrieving");
	} else {
		let milestoneAnswerSession = undefined;
		const response = await getCurrentMilestoneAnswerSession({
			path: { child_id: currentChild.id },
		});

		if (response.error) {
			console.log("Error when retrieving milestone answer session");
			showAlert = true;
			alertMessage =
				$_("milestone.alertMessageRetrieving") + " " + response.error.detail;
			return;
		} else {
			milestoneAnswerSession = response.data;
		}
		console.log("milestoneAnswerSession", milestoneAnswerSession);

		data = contentStore.milestoneGroupData.milestones.map(
			(item: MilestonePublic, idx) => {
				const answer = milestoneAnswerSession.answers[`${item.id}`];
				const complete: boolean =
					answer &&
					answer.answer !== null &&
					answer.answer !== undefined &&
					answer.answer > 0;
				return {
					header: item?.text?.[$locale]?.title ?? "",
					complete: complete,
					summary: item?.text?.[$locale]?.desc ?? "",
					events: {
						onclick: () => {
							activeTabChildren.set("milestone");
							contentStore.milestone = item.id;
							contentStore.milestoneData = item;
							contentStore.milestoneIndex = idx;
						},
					},
					auxilliary: complete ? CheckCircleSolid : ExclamationCircleSolid,
				};
			},
		);
	}

	console.log("done");
}

function createStyle(data: any[]) {
	return data.map((item) => {
		return {
			card: {
				class:
					"m-2 max-w-prose dark:text-white text-white hover:cursor-pointer bg-primary-700 dark:bg-primary-900 hover:bg-primary-800 dark:hover:bg-primary-700",
			},
			auxilliary: {
				class: "w-14 h-14",
				color: item.complete === true ? "green" : "red",
			},
		};
	});
}

let showAlert = $state(false);
let alertMessage = $state($_("milestoneGroup.alertMessageError"));
const promise = setup();
let data = $state([]);

const searchData = [
	{
		label: $_("search.allLabel"),
		placeholder: $_("search.allPlaceholder"),
		filterFunction: searchAll,
	},
	{
		label: $_("search.statusLabel"),
		placeholder: $_("search.statusPlaceholder"),
		filterFunction: searchStatus,
	},
	{
		label: $_("search.answerLabel"),
		placeholder: $_("search.answerPlaceholder"),
		filterFunction: searchAnswer,
	},
	{
		label: $_("search.nameLabel"),
		placeholder: $_("search.namePlaceholder"),
		filterFunction: searchTitle,
	},
	{
		label: $_("search.descriptionLabel"),
		placeholder: $_("search.descriptionPlaceholder"),
		filterFunction: searchDescription,
	},
];

const breadcrumbdata: any[] = [
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: $_("milestone.groupOverviewLabel"),
		onclick: () => {
			activeTabChildren.set("milestoneGroup");
		},
		symbol: RectangleListOutline,
	},
	{
		label: contentStore.milestoneGroupData.text[$locale].title,
		onclick: () => {
			activeTabChildren.set("milestoneOverview");
		},
		symbol: GridOutline,
	},
];
</script>

{#await promise}
	<p>{$_("userData.loadingMessage")}</p>
{:then}
	{#if showAlert}
		<AlertMessage message={alertMessage} />
	{:else}
		<div class="mx-auto flex flex-col p-4 md:rounded-t-lg">
			<Breadcrumbs data={breadcrumbdata} />
			<div class="grid gap-y-4 p-4">
				<GalleryDisplay
					data={data}
					itemComponent={CardDisplay}
					componentProps={createStyle(data)}
					withSearch={true}
					{searchData}
				/>
			</div>
		</div>
	{/if}
{:catch error}
<AlertMessage message={error} />
{/await}
