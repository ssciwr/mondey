<svelte:options runes={true}/>

<script lang="ts">
import type { MilestoneAnswerAnalysis } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { Axis, GroupedBar, XYContainer } from "@unovis/ts";
import { onMount } from "svelte";

let { data = [] }: { data: Array<MilestoneAnswerAnalysis> } = $props();
let container_scores: HTMLDivElement;
let container_diff: HTMLDivElement;

onMount(() => {
	const chart_scores = new XYContainer(
		container_scores,
		{
			components: [
				new GroupedBar<MilestoneAnswerAnalysis>({
					x: (d, i) => i,
					y: (d) => d.answer,
				}),
			],
			xAxis: new Axis<MilestoneAnswerAnalysis>({
				type: "x",
				label: `${i18n.tr.admin.milestone}`,
				tickFormat: (tick: number) => `${data[tick].milestone_id}`,
			}),
			yAxis: new Axis<MilestoneAnswerAnalysis>({
				label: `${i18n.tr.admin.score}`,
			}),
			yDomain: [0, 3],
		},
		data,
	);
	const chart_diff = new XYContainer(
		container_diff,
		{
			components: [
				new GroupedBar<MilestoneAnswerAnalysis>({
					x: (d, i) => i,
					y: (d) => d.answer - d.avg_answer,
					color: "#FF6B7E",
				}),
			],
			xAxis: new Axis<MilestoneAnswerAnalysis>({
				type: "x",
				label: `${i18n.tr.admin.milestone}`,
				tickFormat: (tick: number) => `${data[tick].milestone_id}`,
			}),
			yAxis: new Axis<MilestoneAnswerAnalysis>({
				label: `${i18n.tr.admin.differenceFromAverageScore}`,
			}),
			yDomain: [-3, 3],
		},
		data,
	);
});
</script>

<div class="w-full" bind:this={container_scores}>
</div>
<div class="w-full" bind:this={container_diff}>
</div>
