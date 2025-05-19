<svelte:options runes={true}/>

<script lang="ts">
import {
	getChildMilestoneExpectedAgeRanges,
	postChildMilestoneExpectedAgeRanges,
} from "$lib/client/sdk.gen";
import type { ChildMilestoneExpectedAgeRangeAdmin } from "$lib/client/types.gen";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Label } from "flowbite-svelte";
import { onMount } from "svelte";
import RangeSlider from "svelte-range-slider-pips";

let childAgeRanges = $state([] as ChildMilestoneExpectedAgeRangeAdmin[]);
let childAgeIntervals = $state([
	{ from: 0, to: 11, value: 0 },
	{ from: 12, to: 23, value: 0 },
	{
		from: 24,
		to: 35,
		value: 0,
	},
	{ from: 36, to: 47, value: 0 },
	{ from: 48, to: 72, value: 0 },
]);

async function refreshChildAgeRanges() {
	const { data, error } = await getChildMilestoneExpectedAgeRanges();
	if (error || data === undefined) {
		console.log(error);
	} else {
		childAgeRanges = data;
		// note: the backend allows a min/max value to be set for each child age,
		// for now we simplify this in the frontend to setting a single +/- value for each age interval
		// This can be easily modified in the future here without needing any changes to the backend or database models
		for (let childAgeInterval of childAgeIntervals) {
			childAgeInterval.value =
				childAgeRanges[childAgeInterval.from].max_expected_age -
				childAgeRanges[childAgeInterval.from].child_age;
		}
	}
}

async function saveChildAgeRanges() {
	for (const childAgeInterval of childAgeIntervals) {
		for (let age = childAgeInterval.from; age <= childAgeInterval.to; ++age) {
			childAgeRanges[age].min_expected_age =
				childAgeRanges[age].child_age - childAgeInterval.value;
			childAgeRanges[age].max_expected_age =
				childAgeRanges[age].child_age + childAgeInterval.value;
		}
	}
	const { data, error } = await postChildMilestoneExpectedAgeRanges({
		body: childAgeRanges,
	});
	if (error || data === undefined) {
		console.log(error);
	} else {
		await refreshChildAgeRanges();
	}
}

onMount(refreshChildAgeRanges);
</script>

{#if i18n.locale}
    <h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
        {i18n.tr.admin.milestoneChildAgeRanges}
    </h3>
    <div class="m-2">
        {#each childAgeIntervals as childAgeInterval}
            <div class="grow mb-3">
                <Label>
                    <span class="font-bold text-lg mr-1">{`± ${childAgeInterval.value}`}</span>
                    {`${i18n.tr.admin.monthsForChildrenAged} ${childAgeInterval.from} - ${childAgeInterval.to}`}
                </Label>
                <RangeSlider id="range-steps" min={0} max={36} step={1} pips={true} bind:value={childAgeInterval.value}/>
            </div>
        {/each}
    </div>
    <SaveButton onclick={saveChildAgeRanges}/>
{/if}
