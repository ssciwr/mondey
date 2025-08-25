<svelte:options runes={true} />

<script lang="ts">
import { getMilestoneAgeScores } from "$lib/client/sdk.gen";
import type {
	MilestoneAdmin,
	MilestoneAgeScoreCollectionPublic,
} from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import PlotScoreAge from "$lib/components/DataDisplay/PlotScoreAge.svelte";
import IntegerInput from "$lib/components/DataInput/IntegerInput.svelte";
import { i18n } from "$lib/i18n.svelte";
import { isValidAge } from "$lib/util";
import { Label, Modal } from "flowbite-svelte";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	milestone = $bindable(null),
}: { open: boolean; milestone: MilestoneAdmin | null } = $props();

let scoreCollection = $state(null as MilestoneAgeScoreCollectionPublic | null);
let expected_age_months = $state(0);
let relevant_age_min = $state(0);
let relevant_age_max = $state(0);
let valid = $derived(
	isValidAge(expected_age_months) &&
		isValidAge(relevant_age_min) &&
		isValidAge(relevant_age_max),
);

async function getScores() {
	if (!milestone?.id) {
		return;
	}
	const { data, error } = await getMilestoneAgeScores({
		path: { milestone_id: milestone.id },
	});
	if (error || data === undefined) {
		console.log(error);
	} else {
		scoreCollection = data;
	}
}

onMount(async () => {
	if (milestone) {
		expected_age_months = milestone.expected_age_months;
		relevant_age_min = milestone.relevant_age_min;
		relevant_age_max = milestone.relevant_age_max;
	}
	await getScores();
});

function applyChangesToMilestone() {
	open = false;
	if (milestone) {
		milestone.expected_age_months = expected_age_months;
		milestone.relevant_age_min = relevant_age_min;
		milestone.relevant_age_max = relevant_age_max;
	}
}
</script>

<Modal title={i18n.tr.admin.expectedAgeData} bind:open size="lg" outsideclose>
	{#if scoreCollection}
		<div class="py-1">
			<Label>{i18n.tr.admin.expectedAge}</Label>
            <IntegerInput bind:value={expected_age_months}/>
		</div>
		<div class="py-1">
			<Label>{i18n.tr.admin.minRelevantAge}</Label>
            <IntegerInput bind:value={relevant_age_min}/>
		</div>
        <div class="py-1">
            <Label>{i18n.tr.admin.maxRelevantAge}</Label>
            <IntegerInput bind:value={relevant_age_max}/>
        </div>
		{#key expected_age_months}
			{#key relevant_age_min}
                {#key relevant_age_max}
    				<PlotScoreAge {scoreCollection} {expected_age_months} {relevant_age_min} {relevant_age_max}/>
                {/key}
			{/key}
		{/key}
	{/if}
	<svelte:fragment slot="footer">
		<SaveButton onclick={applyChangesToMilestone} disabled={!valid}/>
		<CancelButton onclick={() => {open = false;}}/>
	</svelte:fragment>
</Modal>
