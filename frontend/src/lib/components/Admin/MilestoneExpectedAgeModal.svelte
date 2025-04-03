<svelte:options runes={true} />

<script lang="ts">
import { getMilestoneAgeScores } from "$lib/client/sdk.gen";
import type { MilestoneAgeScore } from "$lib/client/types.gen";
import PlotScoreAge from "$lib/components/DataDisplay/PlotScoreAge.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Modal } from "flowbite-svelte";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	milestoneId = null,
}: { open: boolean; milestoneId: number | null } = $props();

let scores = $state([] as Array<MilestoneAgeScore>);

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
		scores = data.scores;
	}
}

onMount(async () => {
	await updateAnswerData();
});
</script>

<Modal title={i18n.tr.admin.expectedAgeData} bind:open size="lg" outsideclose>
	{#if scores}
		<PlotScoreAge {scores} />
	{/if}
</Modal>
