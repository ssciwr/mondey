<svelte:options runes={true}/>

<script lang="ts">
import type { MilestoneAgeScore } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import {
	Axis,
	CurveType,
	Line,
	Scale,
	StackedBar,
	XYContainer,
} from "@unovis/ts";
import { onMount } from "svelte";

let { scores = [] }: { scores: Array<MilestoneAgeScore> } = $props();
let container: HTMLDivElement;

onMount(() => {
	const chart = new XYContainer(
		container,
		{
			components: [
				new StackedBar<MilestoneAgeScore>({
					x: (d: MilestoneAgeScore) => d.age,
					y: (d: MilestoneAgeScore) => d.avg_score,
					barMinHeight1Px: true,
					barPadding: 0.0,
				}),
				new Line<MilestoneAgeScore>({
					x: (d: MilestoneAgeScore) => d.age,
					y: (d: MilestoneAgeScore) => d.expected_score,
					lineWidth: 3,
					curveType: CurveType.Step,
					lineDashArray: [5],
					color: "#000000",
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
		scores,
	);
});
</script>

<div class="w-full" bind:this={container}>
</div>
