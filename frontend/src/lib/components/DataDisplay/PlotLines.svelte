<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { type PlotData, type PlotDatum } from "$lib/util";
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

onMount(() => {
	if (!plot_data.keys || plot_data.keys.length === 0) {
		return;
	}
	createChart();
});

function createChart() {
	const lineConfig = {
		x: (d: PlotDatum) => d.age,
		lineWidth: 3,
		curveType: CurveType.Linear,
		interpolateMissingData: true,
	};
	const chart = new XYContainer<PlotDatum>(
		xy_container,
		{
			components: [
				new Line({
					...lineConfig,
					y: plot_data.keys.map((k, i) => {
						return (d) => d[k];
					}),
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
	function toggleItem(item: BulletLegendItemInterface, i: number): void {
		const items = legend.config.items;
		items[i].inactive = !items[i].inactive;
		legend.update({ ...legend.config, items: items });
		chart.updateComponents([
			{
				...lineConfig,
				y: plot_data.keys.map((k, i) => {
					return items[i].inactive ? () => undefined : (d) => d[k];
				}),
			},
		]);
	}
	const legend = new BulletLegend(legend_container, {
		items: plot_data.keys.map((key: string) => ({
			name: key,
			inactive: false,
			pointer: true,
		})),
		onLegendItemClick: toggleItem,
	});
}
</script>

<div class="w-full">
    <div class="w-full" bind:this={legend_container}>
    </div>
    <div class="w-full" bind:this={xy_container}>
    </div>
</div>
