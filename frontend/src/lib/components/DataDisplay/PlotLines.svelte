<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { type PlotDatum } from "$lib/util";
import { Axis, BulletLegend, Line, Scale, XYContainer } from "@unovis/ts";
import { onMount } from "svelte";

let { scores = [] }: { scores: Array<PlotDatum> } = $props();
let legend_container: HTMLDivElement;
let xy_container: HTMLDivElement;

onMount(() => {
	if (!scores || Object.keys(scores).length === 0) {
		return;
	}
	const lines = Object.keys(scores[0]).filter((e) => {
		return e !== "age";
	});
	const legend = new BulletLegend(legend_container, {
		items: lines.map((line) => ({ name: line })),
	});
	const chart = new XYContainer(
		xy_container,
		{
			components: [
				new Line({
					x: (d) => d.age,
					y: lines.map((k) => {
						return (d) => d[k];
					}),
					lineWidth: 3,
				}),
			],
			xAxis: new Axis({
				label: `${i18n.tr.admin.age} (m)`,
				tickValues: [1, 2, 3, 4, 5, 6, 9, 12, 16, 24, 36, 48, 60, 72],
			}),
			yAxis: new Axis({ label: `${i18n.tr.admin.averageScore} (1-4)` }),
			xScale: Scale.scalePow().exponent(0.5),
			xDomain: [1, 72],
			yDomain: [1, 4],
		},
		scores,
	);
});
</script>

<div class="w-full">
    <div class="w-full" bind:this={legend_container}>
    </div>
    <div class="w-full" bind:this={xy_container}>
    </div>
</div>
