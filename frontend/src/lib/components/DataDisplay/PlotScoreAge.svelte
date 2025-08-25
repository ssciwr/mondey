<svelte:options runes={true}/>

<script lang="ts">
import type {
	MilestoneAgeScore,
	MilestoneAgeScoreCollectionPublic,
} from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { Axis, Scale, StackedBar, XYContainer, colors } from "@unovis/ts";
import { onMount } from "svelte";

let {
	scoreCollection,
	expected_age_months,
	relevant_age_min,
	relevant_age_max,
}: {
	scoreCollection: MilestoneAgeScoreCollectionPublic | null;
	expected_age_months: number;
	relevant_age_min: number;
	relevant_age_max: number;
} = $props();
let container: HTMLDivElement;

function mean_score(d: MilestoneAgeScore): number {
	const n = d.c0 + d.c1 + d.c2 + d.c3;
	if (n === 0) {
		return 0; // Return a default value to avoid division by zero
	}
	return (d.c1 + 2 * d.c2 + 3 * d.c3) / n;
}

onMount(() => {
	if (scoreCollection) {
		const chart = new XYContainer(
			container,
			{
				components: [
					new StackedBar<MilestoneAgeScore>({
						x: (d: MilestoneAgeScore) => d.age,
						y: (d: MilestoneAgeScore) => mean_score(d),
						barMinHeight1Px: true,
						barPadding: 0.0,
						color: (d: MilestoneAgeScore) => {
							if (d.age > relevant_age_max || d.age < relevant_age_min) {
								return "#aaaaaa";
							}
							if (d.age === expected_age_months) {
								return colors[5];
							}
							return colors[0];
						},
					}),
				],
				xAxis: new Axis<MilestoneAgeScore>({
					label: `${i18n.tr.admin.age} (m)`,
					tickValues: [0, 1, 2, 3, 4, 5, 6, 9, 12, 16, 24, 36, 48, 60, 72],
				}),
				yAxis: new Axis<MilestoneAgeScore>({
					label: `${i18n.tr.admin.averageScore} (0-3)`,
				}),
				xScale: Scale.scalePow().exponent(0.5),
				xDomain: [0, 72],
				yDomain: [0, 3],
			},
			scoreCollection.scores,
		);
	}
});
</script>

<div class="w-full" bind:this={container}>
</div>
