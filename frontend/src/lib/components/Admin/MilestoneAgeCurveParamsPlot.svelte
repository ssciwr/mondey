<svelte:options runes={true}/>

<script lang="ts">
import type { MilestoneAgeCurveParams } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";

let {
	params,
	maxChildAgeMonths = 72,
}: {
	params: Required<MilestoneAgeCurveParams>;
	maxChildAgeMonths?: number;
} = $props();

// A sample curve, steep enough that the minimum margin visibly widens the relevant
// range at the default settings: it is the milestones with a sharp transition that the
// margin exists for. This is an illustration of what the parameters mean, not real data.
const SAMPLE_MIDPOINT = 18;
const SAMPLE_STEEPNESS = 0.6;
// the plotted age range, chosen to show the whole transition of the sample curve
const AGE_MAX = 36;

const WIDTH = 480;
const HEIGHT = 210;
const MARGIN = { top: 10, right: 104, bottom: 34, left: 42 };
const PLOT_WIDTH = WIDTH - MARGIN.left - MARGIN.right;
const PLOT_HEIGHT = HEIGHT - MARGIN.top - MARGIN.bottom;
// the smallest vertical gap between two threshold labels before they are pushed apart
const LABEL_MIN_GAP = 13;
// the same, horizontally, for the age labels below the axis
const TICK_MIN_GAP = 18;

function meanAnswer(age: number): number {
	return 3 / (1 + Math.exp(-SAMPLE_STEEPNESS * (age - SAMPLE_MIDPOINT)));
}

function ageAtMeanAnswer(mean: number): number {
	return SAMPLE_MIDPOINT + Math.log(mean / (3 - mean)) / SAMPLE_STEEPNESS;
}

function xScale(age: number): number {
	return (
		MARGIN.left + (Math.min(Math.max(age, 0), AGE_MAX) / AGE_MAX) * PLOT_WIDTH
	);
}

function yScale(mean: number): number {
	return MARGIN.top + (1 - Math.min(Math.max(mean, 0), 3) / 3) * PLOT_HEIGHT;
}

// The ages derived from the sample curve, following get_milestone_ages_from_curve
// exactly: the ages at the three thresholds, then the range widened to cover the margin
// either side of the expected age, then clamped to the supported ages.
let ages = $derived.by(() => {
	const expected = ageAtMeanAnswer(params.mean_answer_achieved);
	const [thresholdMin, thresholdMax] = [
		ageAtMeanAnswer(params.mean_answer_relevant_min),
		ageAtMeanAnswer(params.mean_answer_relevant_max),
	].sort((a, b) => a - b);
	const margin = params.min_relevant_age_margin_months;
	const clamp = (age: number) => Math.min(Math.max(age, 0), maxChildAgeMonths);
	return {
		expected: clamp(expected),
		// the part of the range that comes from the thresholds
		thresholdMin: clamp(thresholdMin),
		thresholdMax: clamp(thresholdMax),
		// the range after the margin has widened it
		min: clamp(Math.min(thresholdMin, expected - margin)),
		max: clamp(Math.max(thresholdMax, expected + margin)),
	};
});

let curvePath = $derived.by(() => {
	const points: string[] = [];
	for (let age = 0; age <= AGE_MAX; age += 0.5) {
		points.push(
			`${xScale(age).toFixed(1)},${yScale(meanAnswer(age)).toFixed(1)}`,
		);
	}
	return `M${points.join("L")}`;
});

// The three thresholds, with their labels pushed apart where two of them are close
// enough on the mean answer axis for the text to overlap.
let thresholds = $derived.by(() => {
	const entries = [
		{
			mean: params.mean_answer_relevant_max,
			label: i18n.tr.admin.meanAnswerRelevantMax,
			age: ages.thresholdMax,
		},
		{
			mean: params.mean_answer_achieved,
			label: i18n.tr.admin.meanAnswerAchieved,
			age: ages.expected,
		},
		{
			mean: params.mean_answer_relevant_min,
			label: i18n.tr.admin.meanAnswerRelevantMin,
			age: ages.thresholdMin,
		},
	].map((entry) => ({
		...entry,
		y: yScale(entry.mean),
		labelY: yScale(entry.mean),
	}));
	entries.sort((a, b) => a.labelY - b.labelY);
	for (let i = 1; i < entries.length; i++) {
		const gap = entries[i].labelY - entries[i - 1].labelY;
		if (gap < LABEL_MIN_GAP) {
			entries[i].labelY = entries[i - 1].labelY + LABEL_MIN_GAP;
		}
	}
	return entries;
});

// The derived ages, labelling the age axis. Ages that round to the same month collapse
// to one label, and labels that would still overlap are nudged apart: a steep curve puts
// all three within a month or two of each other.
let ageTicks = $derived.by(() => {
	const ticks: { age: number; months: number; bold: boolean; x: number }[] = [];
	for (const [age, bold] of [
		[ages.expected, true],
		[ages.min, false],
		[ages.max, false],
	] as [number, boolean][]) {
		const months = Math.round(age);
		if (!ticks.some((tick) => tick.months === months)) {
			ticks.push({ age, months, bold, x: xScale(age) });
		}
	}
	ticks.sort((a, b) => a.x - b.x);
	for (let i = 1; i < ticks.length; i++) {
		const gap = ticks[i].x - ticks[i - 1].x;
		if (gap < TICK_MIN_GAP) {
			ticks[i].x = ticks[i - 1].x + TICK_MIN_GAP;
		}
	}
	return ticks;
});

let hoverAge = $state(null as number | null);

function onPointerMove(event: PointerEvent) {
	const svg = event.currentTarget as SVGRectElement;
	const rect = svg.getBoundingClientRect();
	const fraction = (event.clientX - rect.left) / rect.width;
	hoverAge = Math.min(Math.max(fraction, 0), 1) * AGE_MAX;
}
</script>

<figure class="m-0 text-gray-600 dark:text-gray-300">
    <svg viewBox="0 0 {WIDTH} {HEIGHT}" class="w-full" role="img"
         aria-label={i18n.tr.admin.ageCurveParamsPlotDescription}>
        <defs>
            <!-- the part of the range added by the minimum margin is hatched rather than a
                 second colour, so that it reads as the same region, extended -->
            <pattern id="margin-hatch" width="6" height="6" patternTransform="rotate(45)"
                     patternUnits="userSpaceOnUse">
                <line y2="6" stroke="var(--range-color)" stroke-width="2" opacity="0.45"/>
            </pattern>
        </defs>

        <!-- the relevant age range: the ages at which the milestone is asked about -->
        <rect x={xScale(ages.min)} y={MARGIN.top} width={xScale(ages.max) - xScale(ages.min)}
              height={PLOT_HEIGHT} fill="var(--range-color)" opacity="0.14"/>
        {#each [[ages.min, ages.thresholdMin], [ages.thresholdMax, ages.max]] as [from, to]}
            {#if to > from}
                <rect x={xScale(from)} y={MARGIN.top} width={xScale(to) - xScale(from)}
                      height={PLOT_HEIGHT} fill="url(#margin-hatch)"/>
            {/if}
        {/each}

        <!-- mean answer grid -->
        {#each [0, 1, 2, 3] as mean}
            <line x1={MARGIN.left} x2={MARGIN.left + PLOT_WIDTH} y1={yScale(mean)} y2={yScale(mean)}
                  stroke="currentColor" opacity="0.18"/>
            <text x={MARGIN.left - 6} y={yScale(mean) + 3.5} text-anchor="end" font-size="10"
                  fill="currentColor" opacity="0.75">{mean}</text>
        {/each}
        <text transform="rotate(-90)" x={-(MARGIN.top + PLOT_HEIGHT / 2)} y="11" text-anchor="middle"
              font-size="9" fill="currentColor" opacity="0.75">{i18n.tr.admin.averageScore} (0-3)</text>

        <!-- the thresholds the ages are read off the curve at -->
        {#each thresholds as threshold}
            <line x1={MARGIN.left} x2={xScale(threshold.age)} y1={threshold.y} y2={threshold.y}
                  stroke="currentColor" stroke-width="1" stroke-dasharray="4 4" opacity="0.7"/>
            <line x1={xScale(threshold.age)} x2={xScale(threshold.age)} y1={threshold.y}
                  y2={MARGIN.top + PLOT_HEIGHT} stroke="currentColor" stroke-width="1"
                  stroke-dasharray="4 4" opacity="0.7"/>
            <text x={MARGIN.left + PLOT_WIDTH + 6} y={threshold.labelY + 3.5} font-size="9"
                  fill="currentColor" opacity="0.85">{threshold.label.split(" ")[0]} {threshold.mean.toFixed(2)}</text>
        {/each}

        <!-- the sample curve -->
        <path d={curvePath} fill="none" stroke="var(--curve-color)" stroke-width="2"/>

        <!-- the expected age -->
        <circle cx={xScale(ages.expected)} cy={yScale(params.mean_answer_achieved)} r="4"
                fill="var(--curve-color)"/>

        <!-- age axis, labelled with the derived ages -->
        <line x1={MARGIN.left} x2={MARGIN.left + PLOT_WIDTH} y1={MARGIN.top + PLOT_HEIGHT}
              y2={MARGIN.top + PLOT_HEIGHT} stroke="currentColor" opacity="0.4"/>
        {#each ageTicks as tick}
            <text x={tick.x} y={MARGIN.top + PLOT_HEIGHT + 13} text-anchor="middle" font-size="10"
                  font-weight={tick.bold ? 'bold' : 'normal'} fill="currentColor">{tick.months}</text>
        {/each}
        <text x={MARGIN.left + PLOT_WIDTH} y={HEIGHT - 3} text-anchor="end" font-size="9"
              fill="currentColor" opacity="0.75">{i18n.tr.admin.age} (m)</text>

        {#if hoverAge !== null}
            <line x1={xScale(hoverAge)} x2={xScale(hoverAge)} y1={MARGIN.top}
                  y2={MARGIN.top + PLOT_HEIGHT} stroke="currentColor" stroke-width="1" opacity="0.5"/>
            <text x={MARGIN.left + 4} y={MARGIN.top + 10} font-size="10" fill="currentColor">
                {Math.round(hoverAge)} m &rarr; {i18n.tr.admin.meanAnswerShort} {meanAnswer(hoverAge).toFixed(2)}
            </text>
        {/if}

        <rect x={MARGIN.left} y={MARGIN.top} width={PLOT_WIDTH} height={PLOT_HEIGHT}
              fill="transparent" onpointermove={onPointerMove}
              onpointerleave={() => {hoverAge = null;}}/>
    </svg>
    <figcaption class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs">
        <span class="flex items-center gap-1">
            <span class="inline-block h-0.5 w-4" style="background: var(--curve-color)"></span>
            {i18n.tr.admin.sampleAgeCurve}
        </span>
        <span class="flex items-center gap-1">
            <span class="inline-block h-3 w-4 opacity-30" style="background: var(--range-color)"></span>
            {i18n.tr.admin.relevantAgeRange}: {Math.round(ages.min)}&ndash;{Math.round(ages.max)} m
        </span>
        <span class="flex items-center gap-1">
            <span class="inline-block h-3 w-4 border border-dashed opacity-70" style="border-color: var(--range-color)"></span>
            {i18n.tr.admin.marginExtension}
        </span>
        <span>{i18n.tr.admin.expectedAge}: {Math.round(ages.expected)} m</span>
    </figcaption>
</figure>

<style>
    figure {
        --curve-color: #6859be;
        --range-color: #00c19a;
    }

    :global(.dark) figure {
        /* a darker teal keeps the range within the lightness band on a dark surface */
        --range-color: #00a382;
    }
</style>
