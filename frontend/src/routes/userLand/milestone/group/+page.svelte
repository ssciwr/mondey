<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
	getMilestoneGroups,
} from "$lib/client";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { contentStore } from "$lib/stores/contentStore.svelte";
import { Spinner } from "flowbite-svelte";
import {
	GridPlusSolid,
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";

function computeProgress(
	milestones: MilestonePublic[] | undefined,
	answerSession: MilestoneAnswerSessionPublic,
): number {
	if (milestones === undefined) {
		return 0;
	}

	if (milestones.length === 0) {
		return 0;
	}
	const progress = milestones.filter((item) => {
		return (
			item.id in answerSession.answers &&
			answerSession.answers[item.id].answer >= 0
		);
	}).length;
	if (progress < 0.01) {
		return 0.01;
	}
	return progress / milestones.length;
}

async function setup(): Promise<any> {
	if (i18n.locale === undefined || i18n.locale === null) {
		console.log("locale not set");
		return [];
	}

	await currentChild.load_data();

	if (currentChild.id === null || currentChild.id === undefined) {
		console.log("Error when retrieving child data");
		alertStore.showAlert(
			i18n.tr.milestone.alertMessageError,
			i18n.tr.childData.alertMessageRetrieving,
			true,
			false,
		);
		data = [];
		return data;
	}

	const milestonegroups = await getMilestoneGroups({
		path: { child_id: currentChild.id },
	});

	const answerSession = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});

	if (answerSession.error) {
		console.log("Error when retrieving answer data");
		alertStore.showAlert(
			i18n.tr.milestone.alertMessageError,
			i18n.tr.milestone.alertMessageRetrieving + answerSession.error.detail,
			true,
			false,
		);
		data = [];
		return data;
	}

	if (milestonegroups.error) {
		console.log("Error when retrieving milestone group data");
		alertStore.showAlert(
			i18n.tr.milestone.alertMessageError,
			i18n.tr.milestone.alertMessageRetrieving + milestonegroups.error.detail,
			true,
			false,
		);
		data = [];
		return data;
	}

	data = milestonegroups.data.map((item) => {
		const res = {
			header: item.text ? item.text[i18n.locale].title : undefined,
			summary: item.text?.[i18n.locale]?.desc,
			image: null,
			progress: computeProgress(item.milestones, answerSession.data),
			events: {
				onclick: () => {
					goto("/userLand/milestone/overview");
					contentStore.milestoneGroup = item.id;
					contentStore.milestoneGroupData = item;
				},
			},
		};
		return res;
	});

	return data;
}

const breadcrumbdata: any[] = [
	{
		label: i18n.tr.childData.overviewLabel,
		onclick: () => {
			goto("/userLand/children/gallery");
		},
		symbol: GridPlusSolid,
	},
	{
		label: currentChild.name,
		symbol: UserSettingsOutline,
		onclick: () => {
			goto("/userLand/children/registration");
		},
	},
	{
		label: i18n.tr.milestone.groupOverviewLabel,
		symbol: RectangleListOutline,
		onclick: () => {
			goto("/userLand/milestone/group");
		},
	},
];

function searchByStatus(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		// button label contains info about completion status => use for search
		if (key === i18n.tr.search.complete) {
			return item.progress === 1;
		}
		return item.progress < 1;
	});
}

function searchBySurveyDescription(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	return data.filter((item) => {
		return item.summary.toLowerCase().includes(key.toLowerCase());
	});
}

function searchBySurveyTitle(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	}
	const filtered = data.filter((item) => {
		return item.header.toLowerCase().includes(key.toLowerCase());
	});
	return filtered;
}

// README: this is slow and quite a bit of work because a lot of text has to be searched. Kill it?
function searchAll(data: any[], key: string): any[] {
	return [
		...new Set([
			...searchByStatus(data, key),
			...searchBySurveyTitle(data, key),
			...searchBySurveyDescription(data, key),
		]),
	];
}

export function createStyle(data: any[]) {
	return data.map((item) => {
		return {
			card: {
				class:
					"m-2 max-w-prose dark:text-white text-white hover:cursor-pointer bg-milestone-700 dark:bg-milestone-900 hover:bg-milestone-800 dark:hover:bg-milestone-700",
			},
			progress: {
				labelInside: true,
				size: "h-4",
				divClass: `h-full rounded-full w-${100 * item.progress}`,
				color: "red",
				completeColor: "green",
			},
		};
	});
}

let promise = $state(setup());
let data: any[] = $state([]);
const searchData: any[] = [
	{
		label: i18n.tr.search.allLabel,
		placeholder: i18n.tr.search.allPlaceholder,
		filterFunction: searchAll,
	},
	{
		label: i18n.tr.search.descriptionLabel,
		placeholder: i18n.tr.search.descriptionPlaceholder,
		filterFunction: searchBySurveyDescription,
	},
	{
		label: i18n.tr.search.surveyLabel,
		placeholder: i18n.tr.search.surveyPlaceholder,
		filterFunction: searchBySurveyTitle,
	},
	{
		label: i18n.tr.search.statusLabel,
		placeholder: i18n.tr.search.statusPlaceholder,
		filterFunction: searchByStatus,
	},
];

$effect(() => {
	console.log("Data now: ", data);
});
</script>

{#await promise}
    <Spinner /> <p>{i18n.tr.userData.loadingMessage}</p>
{:then data}

    <div class="flex flex-col md:rounded-t-lg">
        <Breadcrumbs data={breadcrumbdata} />
        <div class="grid gap-y-8">
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
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error.message, true, true, () => goto("/userLand/milestone/overview"))}
{/await}
