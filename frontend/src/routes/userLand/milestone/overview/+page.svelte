<svelte:options runes={true}/>
<script lang="ts">
import { goto } from "$app/navigation";
import { getAdminSettings } from "$lib/client";
import {
	type MilestoneAnswerSessionPublic,
	getCurrentMilestoneAnswerSession,
} from "$lib/client";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import WhiteCircle from "$lib/components/WhiteCircle.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { contentStore } from "$lib/stores/contentStore.svelte";
import {
	GridOutline,
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";

async function setup(): Promise<{
	answerSession: MilestoneAnswerSessionPublic | null;
	showCompletion: boolean;
}> {
	if (!currentChild?.id) {
		await goto("/userLand/children");
		return { answerSession: null, showCompletion: true };
	}
	if (
		!contentStore.milestoneGroupData?.milestones ||
		contentStore.milestoneGroupData?.milestones?.length === 0
	) {
		console.log(
			"Error when retrieving milestone groups ",
			contentStore.milestoneGroupData,
		);
		await goto("/userLand/children");
		return { answerSession: null, showCompletion: true };
	}
	await currentChild.load_data();

	let showCompletion = true;
	try {
		const response = await getAdminSettings();
		if (response.data) {
			showCompletion =
				!response.data.hide_milestone_feedback &&
				!response.data.hide_all_feedback;
		}
	} catch (e) {
		console.log(
			"Failed to load admin settings, showing completion indicators by default",
			e,
		);
	}
	const { data, error } = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});
	if (error || !data) {
		console.log("Error when retrieving milestone answer session");
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			i18n.tr.childData.alertMessageRetrieving,
			true,
			true,
		);
		return { answerSession: null, showCompletion: true };
	}
	return { answerSession: data, showCompletion };
}

let showIncompleteOnly = $state(true);

const promise = $state(setup());

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
		label: contentStore.milestoneGroupData?.text?.[i18n.locale]?.title,
		onclick: () => {
			goto("/userLand/milestone/overview");
		},
		symbol: GridOutline,
	},
];
</script>

{#await promise}
    <p>{i18n.tr.userData.loadingMessage}</p>
{:then result}
    {@const answerSession = result?.answerSession}
    {@const showCompletion = result?.showCompletion ?? true}
    <div class="mx-auto flex flex-col md:rounded-t-lg">
        <Breadcrumbs data={breadcrumbdata} stayExpanded={true} />
        <div class="p-4 text-center md:hidden">
            <p class="text-sm text-gray-700 dark:text-gray-400">
                {i18n.tr.milestone.milestoneOverviewMobileHint}
            </p>
        </div>
        <GalleryDisplay showIncompleteTranslation={i18n.tr.milestone.milestonesThatNeedToBeEditedHint} bind:showIncompleteOnly={showIncompleteOnly}>
            {#each contentStore.milestoneGroupData.milestones as milestone, idx}
                {@const title = milestone?.text?.[i18n.locale]?.title ?? ""}
                {@const complete = (answerSession?.answers?.[`${milestone.id}`]?.answer ?? -1) >= 0}
                {#if !(showIncompleteOnly && complete)}
                    <CardDisplay {title}
                                 cardClasses="dark:text-white text-white bg-milestone-300 dark:bg-milestone-300 hover:bg-milestone-500 dark:hover:bg-milestone-500"
                                 titleClasses="text-center"
                                 onclick={() => {
                                    contentStore.milestone = milestone.id;
                                    contentStore.milestoneData = milestone;
                                    contentStore.milestoneIndex = idx;
                                    goto("/userLand/milestone");
                                 }}
                    >
                        {#if showCompletion}
                            <div class="mb-4 flex w-full justify-center">
                                <WhiteCircle solid={complete}/>
                            </div>
                        {/if}
                    </CardDisplay>
                {/if}
            {/each}
        </GalleryDisplay>
    </div>
{:catch error}
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error, true, true)}
{/await}
