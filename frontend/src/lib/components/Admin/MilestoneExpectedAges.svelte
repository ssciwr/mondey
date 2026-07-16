<svelte:options runes={true}/>

<script lang="ts">
import {
	getAdminSettings,
	recalculateMilestoneAgeScores,
	updateMilestone,
} from "$lib/client/sdk.gen";
import type {
	MilestoneAdmin,
	MilestoneAgeCurveParams,
	MilestoneAgeScoreCollectionPublic,
} from "$lib/client/types.gen";
import MilestoneAgeCurveParamsPlot from "$lib/components/Admin/MilestoneAgeCurveParamsPlot.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import PlotScoreAge from "$lib/components/DataDisplay/PlotScoreAge.svelte";
import { i18n } from "$lib/i18n.svelte";
import { milestoneGroups } from "$lib/stores/adminStore.svelte";
import { isValidAge } from "$lib/util";
import {
	Button,
	Input,
	Label,
	Modal,
	Progressbar,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import { RefreshOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let currentMilestone = $state(null as MilestoneAdmin | null);
let showMilestoneExpectedAgeModal = $state(false);
let currentTitle = $state("");
let expectedAges = $state(
	{} as Record<number, MilestoneAgeScoreCollectionPublic>,
);
let calculateProgress = $state(0);
let saveProgress = $state(0);
let calculateError = $state("");

// How the expected age and the relevant age range are derived from each milestone's
// fitted age curve. Defaults are only used until the current values are loaded from the
// backend, which is where they are stored: the ages themselves are not stored anywhere,
// they are derived from the fitted curves at these parameters whenever they are asked for.
let params = $state({
	mean_answer_achieved: 2.4,
	mean_answer_relevant_min: 0.3,
	mean_answer_relevant_max: 2.7,
	min_relevant_age_margin_months: 2,
} as Required<MilestoneAgeCurveParams>);

// Which parameters are invalid, and why. The same rules are enforced by the backend, so
// this is only here to explain the problem before the request is made.
let validation = $derived.by(() => {
	const {
		mean_answer_achieved: achieved,
		mean_answer_relevant_min: relevantMin,
		mean_answer_relevant_max: relevantMax,
		min_relevant_age_margin_months: margin,
	} = params;
	// the curve only approaches 0 and 3 asymptotically, so the age at either of them is
	// infinite: the thresholds have to stay strictly inside that range
	const badMeanAnswer = (mean: number) =>
		!(Number.isFinite(mean) && mean > 0 && mean < 3);
	const badOrder = !(relevantMin < relevantMax);
	// the milestone is only asked about within its relevant age range, so the age at
	// which it is expected to be achieved has to lie inside that range
	const badAchieved = !(relevantMin <= achieved && achieved <= relevantMax);
	const badMargin = !isValidAge(margin);

	const errors: string[] = [];
	if ([achieved, relevantMin, relevantMax].some(badMeanAnswer)) {
		errors.push(i18n.tr.admin.invalidMeanAnswer);
	}
	if (badOrder) {
		errors.push(i18n.tr.admin.invalidRelevantOrder);
	}
	if (badAchieved && !badOrder) {
		errors.push(i18n.tr.admin.invalidAgeCurveParams);
	}
	if (badMargin) {
		errors.push(i18n.tr.admin.invalidAgeMargin);
	}
	return {
		errors,
		valid: errors.length === 0,
		achieved: badMeanAnswer(achieved) || badAchieved,
		relevantMin: badMeanAnswer(relevantMin) || badOrder,
		relevantMax: badMeanAnswer(relevantMax) || badOrder,
		margin: badMargin,
	};
});

onMount(async () => {
	const { data, error } = await getAdminSettings();
	if (error || data === undefined) {
		console.log(error);
		return;
	}
	params = {
		mean_answer_achieved: data.mean_answer_achieved,
		mean_answer_relevant_min: data.mean_answer_relevant_min,
		mean_answer_relevant_max: data.mean_answer_relevant_max,
		min_relevant_age_margin_months: data.min_relevant_age_margin_months,
	};
});

async function getNewExpectedAges() {
	expectedAges = {};
	calculateProgress = 0;
	saveProgress = 0;
	calculateError = "";
	// this only re-derives the ages from the curves fitted by the last statistics
	// update, it does not refit them, so it is a single quick request
	const { data, error } = await recalculateMilestoneAgeScores({ body: params });
	if (error || data === undefined) {
		console.log(error);
		calculateError = i18n.tr.admin.error;
		return;
	}
	for (const collection of data) {
		expectedAges[collection.milestone_id] = collection;
	}
	calculateProgress = 100;
}

async function saveNewExpectedAges() {
	const total = milestoneGroups.data.length;
	const delta = 100.0 / total;
	saveProgress = 0;
	for (const group of milestoneGroups.data) {
		if (group.milestones) {
			for (const milestone of group.milestones) {
				const newAges = expectedAges[milestone.id];
				// a milestone whose age curve could not be fitted has no automatic
				// estimate: leave the ages an admin has set for it alone
				if (
					newAges?.expected_age == null ||
					newAges.relevant_age_min == null ||
					newAges.relevant_age_max == null
				) {
					continue;
				}
				milestone.expected_age_months = newAges.expected_age;
				milestone.relevant_age_min = newAges.relevant_age_min;
				milestone.relevant_age_max = newAges.relevant_age_max;
				const { error } = await updateMilestone({ body: milestone });
				if (error) {
					console.log(error);
					return;
				}
			}
		}
		saveProgress += delta;
	}
	saveProgress = 100;
	await milestoneGroups.refresh();
}
</script>

{#if milestoneGroups.data && i18n.locale}
    <h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
        {i18n.tr.admin.expectedAge}
    </h3>
    <div class="mb-3 grid gap-4 lg:grid-cols-2">
        <div>
            <h4 class="mb-2 text-base font-medium text-gray-900 dark:text-white">{i18n.tr.admin.ageCurveParams}</h4>
            <div class="grid grid-cols-2 gap-3">
                <Label class="space-y-1">
                    <span>{i18n.tr.admin.meanAnswerRelevantMin}</span>
                    <Input type="number" step="0.05" min="0.05" max="2.95" color={validation.relevantMin ? 'red' : undefined}
                           bind:value={params.mean_answer_relevant_min}/>
                </Label>
                <Label class="space-y-1">
                    <span>{i18n.tr.admin.meanAnswerAchieved}</span>
                    <Input type="number" step="0.05" min="0.05" max="2.95" color={validation.achieved ? 'red' : undefined}
                           bind:value={params.mean_answer_achieved}/>
                </Label>
                <Label class="space-y-1">
                    <span>{i18n.tr.admin.meanAnswerRelevantMax}</span>
                    <Input type="number" step="0.05" min="0.05" max="2.95" color={validation.relevantMax ? 'red' : undefined}
                           bind:value={params.mean_answer_relevant_max}/>
                </Label>
                <Label class="space-y-1">
                    <span>{i18n.tr.admin.minRelevantAgeMargin}</span>
                    <Input type="number" step="1" min="0" max="72" color={validation.margin ? 'red' : undefined}
                           bind:value={params.min_relevant_age_margin_months}/>
                </Label>
            </div>
            {#each validation.errors as error}
                <p class="mt-2 text-sm text-red-600 dark:text-red-500">{error}</p>
            {/each}
            {#if calculateError}
                <p class="mt-2 text-sm text-red-600 dark:text-red-500">{calculateError}</p>
            {/if}
        </div>
        <div>
            <h4 class="mb-2 text-base font-medium text-gray-900 dark:text-white">{i18n.tr.admin.ageCurveParamsPlot}</h4>
            {#if validation.valid}
                <MilestoneAgeCurveParamsPlot {params}/>
            {:else}
                <p class="text-sm text-gray-500 dark:text-gray-400">{i18n.tr.admin.ageCurveParamsPlotUnavailable}</p>
            {/if}
        </div>
    </div>
    <div class="grid grid-cols-2 justify-items-stretch">
        <div class="grid grid-rows-2">
            <Button class="btn-primary" disabled={!validation.valid} onclick={getNewExpectedAges}>
                <RefreshOutline class="me-2 h-5 w-5"/> {i18n.tr.admin.recalculateExpectedAge}</Button>
            <div class="m-2">
                <Progressbar labelInside progress={calculateProgress} size="h-4"/>
            </div>
        </div>
        <div class="grid grid-rows-2">
            <SaveButton disabled={calculateProgress < 100} onclick={saveNewExpectedAges}/>
            <div class="m-2">
                <Progressbar labelInside color="green" progress={saveProgress} size="h-4"/>
            </div>
        </div>
    </div>
    <Table>
        <TableHead>
            <TableHeadCell>{i18n.tr.admin.milestones}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.expectedAge}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.newExpectedAge}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each milestoneGroups.data as milestoneGroup (milestoneGroup.id)}
                {@const groupTitle = milestoneGroup.text[i18n.locale].title}
                {#each milestoneGroup.milestones as milestone (milestone.id)}
                    {@const milestoneTitle = `${groupTitle} / ${milestone.text[i18n.locale].title}`}
                    {@const newAges = expectedAges?.[milestone.id]}
                    {@const newExpectedAge = newAges?.expected_age ?? '-'}
                    {@const newRelevantAgeMin = newAges?.relevant_age_min ?? '-'}
                    {@const newRelevantAgeMax = newAges?.relevant_age_max ?? '-'}
                    <TableBodyRow>
                        <TableBodyCell>{milestoneTitle}</TableBodyCell>
                        <TableBodyCell>{milestone.expected_age_months} [{milestone.relevant_age_min}-{milestone.relevant_age_max}]</TableBodyCell>
                        <TableBodyCell>
                            {#if newAges && !newAges.curve_fit_ok}
                                <!-- no age curve could be fitted, so there is no automatic estimate and
                                     the ages set on the milestone are left as they are -->
                                <span class="text-gray-500 dark:text-gray-400">{i18n.tr.admin.noCurveFit} ({newAges.curve_n_answers} {i18n.tr.admin.answersCount})</span>
                            {:else}
                                {newExpectedAge} [{newRelevantAgeMin}-{newRelevantAgeMax}]
                            {/if}
                        </TableBodyCell>
                        <Button class="m-2" disabled={!newAges}
                                onclick={() => {currentMilestone = milestone; currentTitle = `${milestoneTitle} ${i18n.tr.admin.newExpectedAge}: ${newExpectedAge}m [${newRelevantAgeMin}m-${newRelevantAgeMax}m]`; showMilestoneExpectedAgeModal = true;}}>{i18n.tr.admin.data}</Button>
                    </TableBodyRow>
                {/each}
            {/each}
        </TableBody>
    </Table>
{/if}

{#key currentMilestone}
    <Modal title={currentTitle} bind:open={showMilestoneExpectedAgeModal} size="lg" outsideclose>
        {#if currentMilestone}
            {@const newAges = expectedAges?.[currentMilestone.id]}
            <PlotScoreAge scoreCollection={newAges} expected_age_months={newAges?.expected_age ?? null}
                          relevant_age_min={newAges?.relevant_age_min ?? null}
                          relevant_age_max={newAges?.relevant_age_max ?? null} curveParams={params}/>
        {/if}
    </Modal>
{/key}
