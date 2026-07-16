<svelte:options runes={true}/>

<script lang="ts">
import type {
	MilestoneAgeCurveParams,
	MilestoneAgeScore,
	MilestoneAgeScoreCollectionPublic,
} from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { Axis, Line, Scale, StackedBar, XYContainer, colors } from "@unovis/ts";
import { onMount } from "svelte";

let {
	scoreCollection,
	expected_age_months,
	relevant_age_min,
	relevant_age_max,
	curveParams = null,
}: {
	scoreCollection: MilestoneAgeScoreCollectionPublic | null;
	expected_age_months: number | null;
	relevant_age_min: number | null;
	relevant_age_max: number | null;
	// if supplied, the mean answers the ages above are derived from are drawn as
	// reference lines, so it is clear where each one crosses the fitted curve
	curveParams?: MilestoneAgeCurveParams | null;
} = $props();
let container: HTMLDivElement;

function mean_score(d: MilestoneAgeScore): number {
	const n = d.c0 + d.c1 + d.c2 + d.c3;
	if (n === 0) {
		return 0; // Return a default value to avoid division by zero
	}
	return (d.c1 + 2 * d.c2 + 3 * d.c3) / n;
}

// The logistic curve fitted to the answers for this milestone, from which its expected
// age and relevant age range are derived. Returns null if no curve could be fitted, in
// which case there is no automatic estimate of those ages for this milestone and no
// curve to plot.
function fitted_mean_answer(
	collection: MilestoneAgeScoreCollectionPublic,
): ((age: number) => number) | null {
	if (!collection.curve_fit_ok) {
		return null;
	}
	const { curve_midpoint, curve_steepness } = collection;
	return (age: number) =>
		3 / (1 + Math.exp(-curve_steepness * (age - curve_midpoint)));
}

onMount(() => {
	if (scoreCollection) {
		const fittedCurve = fitted_mean_answer(scoreCollection);
		const scoresByAge = [...scoreCollection.scores].sort(
			(a, b) => a.age - b.age,
		);
		const components: (
			| StackedBar<MilestoneAgeScore>
			| Line<MilestoneAgeScore>
		)[] = [
			new StackedBar<MilestoneAgeScore>({
				x: (d: MilestoneAgeScore) => d.age,
				y: (d: MilestoneAgeScore) => mean_score(d),
				barMinHeight1Px: true,
				barPadding: 0.0,
				color: (d: MilestoneAgeScore) => {
					if (relevant_age_min === null || relevant_age_max === null) {
						return colors[0];
					}
					if (d.age > relevant_age_max || d.age < relevant_age_min) {
						return "#aaaaaa";
					}
					if (d.age === expected_age_months) {
						return colors[5];
					}
					return colors[0];
				},
			}),
		];
		if (fittedCurve !== null) {
			components.push(
				new Line<MilestoneAgeScore>({
					x: (d: MilestoneAgeScore) => d.age,
					y: (d: MilestoneAgeScore) => fittedCurve(d.age),
					color: colors[5],
					lineWidth: 2,
				}),
			);
		}
		if (curveParams) {
			// the thresholds the three ages are read off the fitted curve at
			for (const meanAnswer of [
				curveParams.mean_answer_relevant_min,
				curveParams.mean_answer_achieved,
				curveParams.mean_answer_relevant_max,
			]) {
				if (meanAnswer === undefined) {
					continue;
				}
				components.push(
					new Line<MilestoneAgeScore>({
						x: (d: MilestoneAgeScore) => d.age,
						y: () => meanAnswer,
						color: "#aaaaaa",
						lineWidth: 1,
						lineDashArray: [4, 4],
					}),
				);
			}
		}
		const chart = new XYContainer(
			container,
			{
				components: components,
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
			scoresByAge,
		);
	}
});
</script>

<div class="w-full" bind:this={container}>
</div>
