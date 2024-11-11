<script lang="ts">
import { getMilestoneGroups } from "$lib/client";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { createStyle, surveyData } from "$lib/components/MilestoneGroup";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { _ } from "svelte-i18n";

const data: any[] = surveyData;
let showAlert = $state(false);
let alertMessage = $state("");
let promise = $state(setup());

async function setup(): Promise<any> {
	await currentChild.load_data();
	const milestonegroup = await getMilestoneGroups({
		path: { child_id: currentChild.id },
	});

	if (milestonegroup.error) {
		console.log("Error when retrieving milestone group data");
		showAlert = true;
		alertMessage =
			$_("milestone.alertMessageRetrieving") + milestonegroup.error.detail;
	} else {
		console.log(
			"Milestone group data retrieved successfully",
			milestonegroup.data,
		);
	}
}

const breadcrumbdata: any[] = [
	{
		label: $_("childData.overviewLabel"),
		onclick: () => {
			activeTabChildren.set("childrenGallery");
		},
	},
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
	},
	{
		label: $_("milestone.groupOverviewLabel"),
		onclick: () => {
			activeTabChildren.set("milestoneGroup");
		},
	},
];

interface MilestoneData {
	number: 4;
	title: string;
	desc: string;
	observation: string;
	help: string;
	answer: string;
}

interface DataElement {
	header: string;
	summary: string;
	milestoneData: any;
	progress: number;
	[key: string]: any;
}

function searchByStatus(data: DataElement[], key: string): DataElement[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			// button label contains info about completion status => use for search
			if (key === "fertig") {
				return item.progress === 1;
			} else if (key === "unfertig") {
				return item.progress < 1;
			} else {
				return item.header.toLowerCase().includes(key.toLowerCase());
			}
		});
	}
}

function searchBySurvey(data: DataElement[], key: string): DataElement[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.header.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchBySurveyDescription(
	data: DataElement[],
	key: string,
): DataElement[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.summary.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchByMilestone(data: DataElement[], key: string): DataElement[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.milestoneData.some((element: MilestoneData) =>
				element.title.toLowerCase().includes(key.toLowerCase()),
			);
		});
	}
}

// README: this is slow and quite a bit of work because a lot of text has to be searched. Kill it?
function searchAll(data: DataElement[], key: string): DataElement[] {
	return [
		...new Set([
			...searchBySurvey(data, key),
			...searchByStatus(data, key),
			...searchByMilestone(data, key),
			...searchBySurveyDescription(data, key),
		]),
	];
}

const searchData: any[] = [
	{
		label: "Alle",
		placeholder: "Alle Kategorien durchsuchen",
		filterFunction: searchAll,
	},
	{
		label: "Bereich",
		placeholder: "Nach Beobachtungsbereich suchen",
		filterFunction: searchBySurvey,
	},
	{
		label: "Bereichsbeschreibung",
		placeholder: "Beschreibung von Bereichen durchsuchen",
		filterFunction: searchBySurveyDescription,
	},
	{
		label: "Meilensteine",
		placeholder: "Nach Meilenstein suchen",
		filterFunction: searchByMilestone,
	},
	{
		label: "Status",
		placeholder: "Bereiche nach Status durchsuchen (fertig/unfertig)",
		filterFunction: searchByStatus,
	},
];
</script>

{#await promise}
<p>{"Waiting for setup to finish"}</p>
{:then milestonedata}
<div class="flex flex-col border border-gray-200 md:rounded-t-lg dark:border-gray-700">
	<Breadcrumbs data={breadcrumbdata} />
	<div class="grid gap-y-8">
		<GalleryDisplay
			data={data.sort((a, b) => a.progress - b.progress)}
			itemComponent={CardDisplay}
			componentProps={createStyle(data)}
			withSearch={true}
			{searchData}
		/>
	</div>
</div>
{:catch error}
{/await}
