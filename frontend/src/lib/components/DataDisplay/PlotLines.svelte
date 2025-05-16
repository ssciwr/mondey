<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { type PlotData } from "$lib/util";
import {
	Axis,
	BulletLegend,
	type BulletLegendItemInterface,
	CurveType,
	Line,
	Scale,
	XYContainer,
} from "@unovis/ts";
import { onMount } from "svelte";

let { plot_data = { keys: [], data: [] } }: { plot_data: PlotData } = $props();
let legend_container: HTMLDivElement;
let xy_container: HTMLDivElement;
let legendItems = $state([] as BulletLegendItemInterface[]);
let chart: XYContainer | null = $state(null);

onMount(() => {
	if (!plot_data.keys || plot_data.keys.length === 0) {
		return;
	}

	legendItems = plot_data.keys.map((key: string) => ({
		name: key,
		inactive: false,
		pointer: true,
	}));

	createChart();

	new BulletLegend(legend_container, {
		items: legendItems,
		onLegendItemClick: handleLegendClick,
	});
});

function handleLegendClick(item: BulletLegendItemInterface, index: number) {
	legendItems[index].inactive = !legendItems[index].inactive;

	while (legend_container.firstChild) {
		legend_container.removeChild(legend_container.firstChild);
	}

	// reuse the clickhandler to keep it responsive
	new BulletLegend(legend_container, {
		items: legendItems.map((item) => ({
			...item,
			pointer: true,
		})),
		onLegendItemClick: handleLegendClick,
	});

	createChart();
}

function createChart() {
	// Destroy existing chart if any (needed because of it becoming out of date/freezing and not responding to onClicks)
	if (chart) {
		chart.destroy();
	}

	chart = new XYContainer(
		xy_container,
		{
			components: [
				new Line({
					x: (d) => d.age,
					y: plot_data.keys.map((k, i) => {
						return legendItems[i].inactive ? () => null : (d) => d[k];
					}),
					lineWidth: 3,
					curveType: CurveType.Linear,
					interpolateMissingData: true,
				}),
			],
			xAxis: new Axis({
				label: `${i18n.tr.admin.age} (m)`,
				tickValues: [1, 2, 3, 4, 5, 6, 9, 12, 16, 24, 36, 48, 60, 72],
			}),
			yAxis: new Axis({ label: `${i18n.tr.admin.averageScore} (0-3)` }),
			xScale: Scale.scalePow().exponent(0.5),
			xDomain: [1, 72],
			yDomain: [0, 3],
		},
		plot_data.data,
	);
}
</script>

<div class="w-full">
    <div class="w-full" bind:this={legend_container}>
    </div>
    <div class="w-full" bind:this={xy_container}>
    </div>
</div>
