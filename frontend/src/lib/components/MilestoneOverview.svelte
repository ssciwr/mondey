<script lang="ts">
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import { convertData, data } from "$lib/components/MilestoneOverview";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";

export let milestones = data.milestones;

interface MilestoneData {
	header: string;
	href: string;
	summary: string;
	auxilliary: string;
	complete: boolean;
	answer: string;
}

function searchStatus(data: MilestoneData[], key: string): MilestoneData[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			// button label contains info about completion status => use for search
			if (key === "fertig") {
				return item.complete === true;
			} else if (key === "unfertig") {
				return item.complete === false;
			}
		});
	}
}

function searchDescription(
	data: MilestoneData[],
	key: string,
): MilestoneData[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.summary.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchTitle(data: MilestoneData[], key: string): MilestoneData[] {
	if (key === "") {
		return data;
	} else {
		return data.filter((item) => {
			return item.header.toLowerCase().includes(key.toLowerCase());
		});
	}
}

function searchAnswer(data: MilestoneData[], key: string): MilestoneData[] {
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

function searchAll(data: MilestoneData[], key: string): MilestoneData[] {
	return [
		...new Set([
			...searchDescription(data, key),
			...searchStatus(data, key),
			...searchTitle(data, key),
			...searchAnswer(data, key),
		]),
	];
}
const searchData = [
	{
		label: "Alle",
		placeholder: "Alle Kategorien durchsuchen",
		filterFunction: searchAll,
	},
	{
		label: "Status",
		placeholder: "Nach Status durchsuchen",
		filterFunction: searchStatus,
	},
	{
		label: "Anwort",
		placeholder: "Nach Antwort durchsuchen",
		filterFunction: searchAnswer,
	},
	{
		label: "Titel",
		placeholder: "Nach Meilenstein durchsuchen",
		filterFunction: searchTitle,
	},
	{
		label: "Beschreibung",
		placeholder: "Beschreibungen durchsuchen",
		filterFunction: searchDescription,
	},
];

const breadcrumbdata: any[] = [
	{
		label: "Benutzer",
		onclick: () => {
			activeTabChildren.update((_) => {
				return "";
			});
		},
	},
	{
		label: "Kinderübersicht",
		onclick: () => {
			activeTabChildren.update((value) => {
				return "childrenGallery";
			});
		},
	},
	{
		label: "Meike",
		onclick: () => {
			activeTabChildren.update((value) => {
				return "childrenDataInput";
			});
		},
	},
	{
		label: "Bereichsübersicht",
		onclick: () => {
			activeTabChildren.update((value) => {
				return "milestoneGroup";
			});
		},
	},
	{
		label: `Grobmotorik`,
		// href: `${base}/milestone`,
		onclick: () => {
			activeTabChildren.update((value) => {
				return "milestone";
			});
		},
	},
];

const rawdata = convertData(milestones).sort((a, b) => a.complete - b.complete); // FIXME: the convert step should not be here and will be handeled backend-side
</script>

<div class="mx-auto flex flex-col border border-gray-200 p-4 md:rounded-t-lg dark:border-gray-700">
	<Breadcrumbs data={breadcrumbdata} />
	<div class="grid gap-y-4 p-4">
		<GalleryDisplay
			data={rawdata}
			itemComponent={CardDisplay}
			componentProps={rawdata.map((item) => {
				return {
					card: {
						class: 'text-gray-700 hover:bg-gray-100'
					},

					auxilliary: {
						class: 'w-14 h-14',
						color: item.complete === true ? '#4ade80' : '#EB4F27'
					}
				};
			})}
			withSearch={true}
			{searchData}
		/>
	</div>
</div>
