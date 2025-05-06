<svelte:options runes={true} />

<script lang="ts">
import { getMilestoneAgeScores } from "$lib/client/sdk.gen";
import type {
	MilestoneAgeScore,
	MilestoneAgeScoreCollectionPublic,
} from "$lib/client/types.gen";
import PlotScoreAge from "$lib/components/DataDisplay/PlotScoreAge.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Modal } from "flowbite-svelte";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	milestoneId = null,
}: { open: boolean; milestoneId: number | null } = $props();

let scoreCollection = $state(null as MilestoneAgeScoreCollectionPublic | null);

async function updateAnswerData() {
	if (!milestoneId) {
		return;
	}
	const { data, error } = await getMilestoneAgeScores({
		path: { milestone_id: milestoneId },
	});
	if (error || data === undefined) {
		console.log(error);
	} else {
		scoreCollection = data;
	}
}

onMount(async () => {
	await updateAnswerData();
});
</script>

<Modal title={i18n.tr.admin.expectedAgeData} bind:open size="lg" outsideclose>
	{#if scoreCollection}
		<PlotScoreAge {scoreCollection} />
	{/if}
</Modal>
