<svelte:options runes={true}/>

<script lang="ts">
import type { MilestoneAnswerAnalysis } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { Axis, GroupedBar, Tooltip, XYContainer, colors } from "@unovis/ts";
import { onMount } from "svelte";

let { data = [] }: { data: Array<MilestoneAnswerAnalysis> } = $props();
let container_scores: HTMLDivElement;
let container_diff: HTMLDivElement;

type ChartDatum = MilestoneAnswerAnalysis & {
	chart_x: number;
	group_color: string;
};

const GROUP_GAP = 1;

function milestoneGroupName(datum: MilestoneAnswerAnalysis): string {
	return datum.milestone_group_name[i18n.locale];
}

function milestoneTitle(datum: MilestoneAnswerAnalysis): string {
	return datum.milestone_title[i18n.locale];
}

function tooltipContent(datum: ChartDatum): HTMLElement {
	const content = document.createElement("div");
	content.className = "p-1";
	content.textContent = milestoneTitle(datum);

	return content;
}

onMount(() => {
	const sortedData = [...data].sort(
		(a, b) =>
			a.milestone_group_order - b.milestone_group_order ||
			a.milestone_group_id - b.milestone_group_id ||
			a.milestone_order - b.milestone_order ||
			a.milestone_id - b.milestone_id,
	);
	const groupIndexes = new Map<number, number>();
	const groups: Array<{ name: string; positions: Array<number> }> = [];
	const chartData: Array<ChartDatum> = sortedData.map((datum, index) => {
		let groupIndex = groupIndexes.get(datum.milestone_group_id);
		if (groupIndex === undefined) {
			groupIndex = groupIndexes.size;
			groupIndexes.set(datum.milestone_group_id, groupIndex);
			groups.push({ name: milestoneGroupName(datum), positions: [] });
		}
		const chartX = index + groupIndex * GROUP_GAP;
		groups[groupIndex].positions.push(chartX);
		return {
			...datum,
			chart_x: chartX,
			group_color: colors[groupIndex % colors.length],
		};
	});
	const groupTicks = groups.map(({ name, positions }) => ({
		position: (positions[0] + positions[positions.length - 1]) / 2,
		label: name,
	}));
	const groupTickLabels = new Map(
		groupTicks.map(({ position, label }) => [position, label]),
	);
	const xAxis = () =>
		new Axis<ChartDatum>({
			type: "x",
			label: `${i18n.tr.admin.milestoneGroup}`,
			tickValues: groupTicks.map(({ position }) => position),
			tickFormat: (tick: number) => groupTickLabels.get(tick) ?? "",
			tickTextWidth: 120,
			tickTextForceWordBreak: true,
		});
	const bar = (y: (datum: ChartDatum) => number) =>
		new GroupedBar<ChartDatum>({
			x: (datum) => datum.chart_x,
			y,
			color: (datum) => datum.group_color,
			dataStep: 1,
		});
	const tooltip = () =>
		new Tooltip({
			triggers: {
				[GroupedBar.selectors.bar]: (datum: ChartDatum) =>
					tooltipContent(datum),
			},
		});

	const chart_scores = new XYContainer(
		container_scores,
		{
			components: [bar((datum) => datum.answer)],
			xAxis: xAxis(),
			yAxis: new Axis<ChartDatum>({
				label: `${i18n.tr.admin.score}`,
			}),
			tooltip: tooltip(),
			yDomain: [0, 3],
		},
		chartData,
	);
	const chart_diff = new XYContainer(
		container_diff,
		{
			components: [bar((datum) => datum.answer - datum.avg_answer)],
			xAxis: xAxis(),
			yAxis: new Axis<ChartDatum>({
				label: `${i18n.tr.admin.differenceFromAverageScore}`,
			}),
			tooltip: tooltip(),
			yDomain: [-3, 3],
		},
		chartData,
	);

	return () => {
		chart_scores.destroy();
		chart_diff.destroy();
	};
});
</script>

<div class="text-center">
<h4>{i18n.tr.admin.score}</h4>
<div class="w-full" bind:this={container_scores}>
</div>
</div>
<hr />
<div class="text-center">
<h4>{i18n.tr.admin.differenceFromAverageScore}</h4>
<div class="w-full" bind:this={container_diff}>
</div>
</div>
