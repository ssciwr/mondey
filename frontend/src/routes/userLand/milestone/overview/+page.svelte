<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import {
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
} from "$lib/client";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { contentStore } from "$lib/stores/contentStore.svelte";
import {
	CheckCircleSolid,
	ExclamationCircleSolid,
	GridOutline,
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";

function searchStatus(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		// button label contains info about completion status => use for search
		if (key === i18n.tr.milestone.complete.toLowerCase()) {
			return item.complete === true;
		}
		return item.complete === false;
	});
}

function searchDescription(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		return item.summary.toLowerCase().includes(key.toLowerCase());
	});
}

function searchTitle(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		return item.header.toLowerCase().includes(key.toLowerCase());
	});
}

function searchAnswer(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		return item.answer === null
			? false
			: item.answer.toLowerCase().includes(key.toLowerCase());
	});
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

	if (i18n.locale === undefined || i18n.locale === null) {
		alertStore.showAlert(
			i18n.tr.userData.alertMessageError,
			i18n.tr.userData.alertMessageError,
			true,
		);
		console.log("No locale");
		return;
	}

	await currentChild.load_data();
	if (
		!contentStore.milestoneGroupData.milestones ||
		contentStore.milestoneGroupData.milestones.length === 0
	) {
		console.log(
			"Error when retrieving milestone groups ",
			contentStore.milestoneGroupData,
		);
		const message =
			contentStore.milestoneGroupData.milestones.length === 0
				? i18n.tr.milestone.alertMessageNoRelevantMilestones
				: i18n.tr.milestone.alertMessageRetrieving;
		alertStore.showAlert(i18n.tr.milestone.alertMessageError, message, true);
	} else {
		let milestoneAnswerSession = undefined;
		const response = await getCurrentMilestoneAnswerSession({
			path: { child_id: currentChild.id },
		});

		if (response.error) {
			console.log("Error when retrieving milestone answer session");
			alertStore.showAlert(
				i18n.tr.milestone.alertMessageError,
				`${i18n.tr.milestone.alertMessageRetrieving} ${response.error.detail}`,
				true,
			);
			return;
		}

		milestoneAnswerSession = response.data;

		console.log("milestoneAnswerSession", milestoneAnswerSession);

		data = contentStore.milestoneGroupData.milestones.map(
			(item: MilestonePublic, idx: number) => {
				const answer = milestoneAnswerSession.answers[`${item.id}`];
				const complete: boolean =
					answer &&
					answer.answer !== null &&
					answer.answer !== undefined &&
					answer.answer >= 0;
				return {
					header: item?.text?.[i18n.locale]?.title ?? "",
					complete: complete,
					summary: item?.text?.[i18n.locale]?.desc ?? "",
					events: {
						onclick: () => {
							contentStore.milestone = item.id;
							contentStore.milestoneData = item;
							contentStore.milestoneIndex = idx;
							goto("/userLand/milestone");
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
					"m-2 max-w-prose dark:text-white text-white hover:cursor-pointer bg-milestone-300 dark:bg-milestone-300 hover:bg-milestone-500 dark:hover:bg-milestone-500",
			},
			auxilliary: {
				class: "w-14 h-14",
				color: item.complete === true ? "green" : "red",
			},
		};
	});
}

const promise = setup();
let data = $state([]);

const searchData = [
	{
		label: i18n.tr.search.allLabel,
		placeholder: i18n.tr.search.allPlaceholder,
		filterFunction: searchAll,
	},
	{
		label: i18n.tr.search.statusLabel,
		placeholder: i18n.tr.search.statusPlaceholder,
		filterFunction: searchStatus,
	},
	{
		label: i18n.tr.search.answerLabel,
		placeholder: i18n.tr.search.answerPlaceholder,
		filterFunction: searchAnswer,
	},
	{
		label: i18n.tr.search.nameLabel,
		placeholder: i18n.tr.search.namePlaceholder,
		filterFunction: searchTitle,
	},
	{
		label: i18n.tr.search.descriptionLabel,
		placeholder: i18n.tr.search.descriptionPlaceholder,
		filterFunction: searchDescription,
	},
];

const breadcrumbdata: any[] = [
	{
		label: currentChild.name,
		onclick: () => {
			goto("/userLand/children/registration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: i18n.tr.milestone.groupOverviewLabel,
		onclick: () => {
			goto("/userLand/milestone/group");
		},
		symbol: RectangleListOutline,
	},
	{
		label: contentStore.milestoneGroupData.text[i18n.locale].title,
		onclick: () => {
			goto("/userLand/milestone/overview");
		},
		symbol: GridOutline,
	},
];
</script>

{#await promise}
    <p>{i18n.tr.userData.loadingMessage}</p>
{:then}
    <div class="mx-auto flex flex-col md:rounded-t-lg">
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
{:catch error}
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error, true, true)}
{/await}
