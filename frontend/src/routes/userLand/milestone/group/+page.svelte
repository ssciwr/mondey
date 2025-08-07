<svelte:options runes={true}/>
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
import Progress from "$lib/components/DataDisplay/Progress.svelte";
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
	const answeredMilestones = milestones.filter((item) => {
		return (
			item.id in answerSession.answers &&
			answerSession.answers[item.id].answer >= 0
		);
	}).length;
	return answeredMilestones / milestones.length;
}

type MilestoneGroupDisplayData = {
	title: string;
	text: string;
	progress: number;
	onclick: () => void;
	disabled: boolean;
};

async function setup(): Promise<MilestoneGroupDisplayData[] | null> {
	await currentChild.load_data();

	if (currentChild.id === null || currentChild.id === undefined) {
		console.log("Error when retrieving child data");
		await goto("/userLand/children");
		return;
	}

	const milestoneGroups = await getMilestoneGroups({
		path: { child_id: currentChild.id },
	});

	if (milestoneGroups.error) {
		console.log("Error when retrieving milestone group data");
		alertStore.showAlert(
			i18n.tr.milestone.alertMessageError,
			i18n.tr.milestone.alertMessageRetrieving + milestoneGroups.error.detail,
			true,
			false,
		);
		return null;
	}

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
		return null;
	}

	return milestoneGroups.data.map((item) => {
		return {
			title: item?.text?.[i18n.locale]?.title ?? "",
			text: item?.text?.[i18n.locale]?.desc ?? "",
			progress: computeProgress(item.milestones, answerSession.data),
			disabled: item.milestones.length === 0,
			onclick: () => {
				goto("/userLand/milestone/overview");
				contentStore.milestoneGroup = item.id;
				contentStore.milestoneGroupData = item;
			},
		};
	});
}

const breadcrumbdata: any[] = [
	{
		label: i18n.tr.childData.overviewLabel,
		onclick: () => {
			goto("/userLand/children");
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

let promise = $state(setup());
let showIncompleteOnly = $state(true);
</script>

{#await promise}
    <Spinner/>
    <p>{i18n.tr.userData.loadingMessage}</p>
{:then milestoneGroups}
    {#if milestoneGroups}
        <div class="flex flex-col md:rounded-t-lg">
            <Breadcrumbs data={breadcrumbdata}/>
            <h3>{i18n.tr.milestone.milestoneGroupSelectionHint}</h3>
            <GalleryDisplay showIncompleteTranslation={i18n.tr.milestone.milestonesThatNeedToBeEditedHint} bind:showIncompleteOnly={showIncompleteOnly}>
                {#each milestoneGroups as milestoneGroup}
                    {#if !(showIncompleteOnly && (milestoneGroup.disabled || milestoneGroup.progress === 1.0))}
                        <CardDisplay title={milestoneGroup.title}
                                     text={milestoneGroup.text}
                                     onclick={milestoneGroup.onclick}
                                     disabled={milestoneGroup.disabled}
                                     cardClasses={`dark:text-white text-white bg-milestone-700 dark:bg-milestone-900 ${milestoneGroup.disabled ? '' : 'hover:bg-milestone-800 dark:hover:bg-milestone-700'}`}
                        >
                            <Progress progress={milestoneGroup.progress} color="#556499"/>
                        </CardDisplay>
                    {/if}
                {/each}
            </GalleryDisplay>
        </div>
    {/if}
{:catch error}
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error.message, true, true, () => goto("/userLand/milestone/overview"))}
{/await}
