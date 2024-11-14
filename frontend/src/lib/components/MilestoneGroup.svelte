<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
	getMilestoneGroups,
} from "$lib/client";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { contentStore } from "$lib/stores/contentStore.svelte";
import { Spinner } from "flowbite-svelte";
import {
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

function computeProgress(
	milestones: MilestonePublic[],
	answerSession: MilestoneAnswerSessionPublic,
): number {
	if (milestones.length === 0) {
		return 0;
	} else {
		const progress = milestones.filter((item) => {
			return (
				item.id in answerSession.answers &&
				answerSession.answers[item.id].answer >= 0
			);
		}).length;
		if (progress < 0.01) {
			return 0.01;
		} else {
			return progress / milestones.length;
		}
	}
}

async function setup(): Promise<any> {
	await currentChild.load_data();
	console.log("currentChild", currentChild);
	console.log("child data: ", currentChild.name);
	const milestonegroups = await getMilestoneGroups({
		path: { child_id: currentChild.id },
	});

	const answerSession = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});

	if (answerSession.error) {
		console.log("Error when retrieving answer data");
		showAlert = true;
		alertMessage =
			$_("milestone.alertMessageRetrieving") + answerSession.error.detail;
		data = [];
		return data;
	}

	if (milestonegroups.error) {
		console.log("Error when retrieving milestone group data");
		showAlert = true;
		alertMessage =
			$_("milestone.alertMessageRetrieving") + milestonegroups.error.detail;

		data = [];
		return data;
	} else {
		console.log(
			"Milestone group data retrieved successfully",
			milestonegroups.data,
		);

		data = milestonegroups.data.map((item) => {
			const res = {
				header: item.text[$locale].title,
				summary: item.text[$locale].desc,
				image: null,
				progress: computeProgress(item.milestones, answerSession.data),
				events: {
					onclick: () => {
						activeTabChildren.set("milestoneOverview");
						contentStore.milestoneGroup = item.id;
						contentStore.milestoneGroupData = item;
					},
				},
			};
			return res;
		});

		return data;
	}
}

const breadcrumbdata: any[] = [
	{
		label: currentChild.name,
		symbol: UserSettingsOutline,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
	},
	{
		label: $_("milestone.groupOverviewLabel"),
		symbol: RectangleListOutline,
	},
];

function searchByStatus(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			// button label contains info about completion status => use for search
			if (key === $_("search.complete")) {
				return item.progress === 1;
			} else {
				return item.progress < 1;
			}
		});
	}
}

function searchBySurveyDescription(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.summary.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchBySurveyTitle(data: any[], key: string): any[] {
	if (key === "") {
		return data;
	} else {
		const filtered = data.filter((item) => {
			return item.header.toLowerCase().includes(key.toLowerCase());
		});
		return filtered;
	}
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
					"m-2 max-w-prose dark:text-white text-white hover:cursor-pointer bg-primary-700 dark:bg-primary-900 hover:bg-primary-800 dark:hover:bg-primary-700",
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

let showAlert = $state(false);
let alertMessage = $state("");
let promise = $state(setup());
let data: any[] = $state([]);
const searchData: any[] = [
	{
		label: $_("search.allLabel"),
		placeholder: $_("search.allPlaceholder"),
		filterFunction: searchAll,
	},
	{
		label: $_("search.descriptionLabel"),
		placeholder: $_("search.descriptionPlaceholder"),
		filterFunction: searchBySurveyDescription,
	},
	{
		label: $_("search.surveyLabel"),
		placeholder: $_("search.surveyPlaceholder"),
		filterFunction: searchBySurveyTitle,
	},
	{
		label: $_("search.statusLabel"),
		placeholder: $_("search.statusPlaceholder"),
		filterFunction: searchByStatus,
	},
];
</script>

{#await promise}
<Spinner /> <p>{$_("userData.loadingMessage")}</p>
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
<AlertMessage message={$_("milestone.alertMessageError") + " "+ error} />
{/await}
