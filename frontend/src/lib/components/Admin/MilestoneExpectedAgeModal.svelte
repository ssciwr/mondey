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
import { i18n } from "$lib/i18n.svelte";
import { Label, Modal } from "flowbite-svelte";
import { onMount } from "svelte";
import { RangeSlider } from "svelte-range-slider-pips";

let {
	open = $bindable(false),
	milestone = $bindable(null),
}: { open: boolean; milestone: MilestoneAdmin | null } = $props();

let scoreCollection = $state(null as MilestoneAgeScoreCollectionPublic | null);
let expected_age_months = $state(0);
let expected_age_delta = $state(0);

async function updateAnswerData() {
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
		expected_age_delta = milestone.expected_age_delta;
	}
	await updateAnswerData();
});

function saveChanges() {
	open = false;
	if (milestone) {
		milestone.expected_age_months = expected_age_months;
		milestone.expected_age_delta = expected_age_delta;
	}
}
</script>

<Modal title={i18n.tr.admin.expectedAgeData} bind:open size="lg" outsideclose>
	{#if scoreCollection}
		<div class="py-1">
			<Label>{`${i18n.tr.admin.expectedAge}: ${expected_age_months}m`}</Label>
			<RangeSlider id="expectedAge-months" min={1} max={72} step={1} pips={true} bind:value={expected_age_months}/>
		</div>
		<div class="py-1">
			<Label>{`${i18n.tr.admin.ageRange}: ± ${expected_age_delta}m`}</Label>
			<RangeSlider id="expectedAgeDelta" min={0} max={72} step={1} pips={true} bind:value={expected_age_delta}/>
		</div>
		{#key expected_age_months}
			{#key expected_age_delta}
				<PlotScoreAge {scoreCollection} {expected_age_months} {expected_age_delta}/>
			{/key}
		{/key}
	{/if}
	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges}/>
		<CancelButton onclick={() => {open = false;}}/>
	</svelte:fragment>
</Modal>
