<svelte:options runes={true}/>
<script lang="ts">
import { goto } from "$app/navigation";
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

async function setup(): Promise<MilestoneAnswerSessionPublic | null> {
	if (!currentChild?.id) {
		await goto("/userLand/children");
		return null;
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
		return null;
	}
	await currentChild.load_data();
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
		return null;
	}
	return data;
}

let searchTerm = $state("");

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
{:then answerSession}
    <div class="mx-auto flex flex-col md:rounded-t-lg">
        <Breadcrumbs data={breadcrumbdata}/>
        <GalleryDisplay bind:searchTerm={searchTerm}>
            {#each contentStore.milestoneGroupData.milestones as milestone, idx}
                {@const title = milestone?.text?.[i18n.locale]?.title ?? ""}
                {@const complete = (answerSession?.answers?.[`${milestone.id}`]?.answer ?? -1) >= 0}
                {#if title.toLowerCase().includes(searchTerm.toLowerCase())}
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
                        <div class="mb-4 flex w-full justify-center">
                            <WhiteCircle solid={complete}/>
                        </div>
                    </CardDisplay>
                {/if}
            {/each}
        </GalleryDisplay>
    </div>
{:catch error}
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error, true, true)}
{/await}
