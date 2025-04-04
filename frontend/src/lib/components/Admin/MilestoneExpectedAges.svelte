<svelte:options runes={true}/>

<script lang="ts">
import { refreshMilestoneGroups } from "$lib/admin.svelte";
import { getMilestoneAgeScores, updateMilestone } from "$lib/client/sdk.gen";
import type { MilestoneAgeScoreCollectionPublic } from "$lib/client/types.gen";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import PlotScoreAge from "$lib/components/DataDisplay/PlotScoreAge.svelte";
import { i18n } from "$lib/i18n.svelte";
import { milestoneGroups } from "$lib/stores/adminStore";
import {
	Button,
	Card,
	Modal,
	Progressbar,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import RefreshOutline from "flowbite-svelte-icons/RefreshOutline.svelte";

let currentMilestoneId = $state(null as number | null);
let showMilestoneExpectedAgeModal = $state(false);
let currentTitle = $state("");
let expectedAges = $state(
	{} as Record<number, MilestoneAgeScoreCollectionPublic>,
);
let calculateProgress = $state(0);
let saveProgress = $state(0);

async function getNewExpectedAge(milestoneId: number) {
	const { data, error } = await getMilestoneAgeScores({
		path: { milestone_id: milestoneId },
	});
	if (error || data === undefined) {
		console.log(error);
	} else {
		expectedAges[milestoneId] = data;
	}
}

async function getNewExpectedAges() {
	expectedAges = {};
	const total = $milestoneGroups.length;
	const delta = 1.0 / total;
	calculateProgress = 0;
	saveProgress = 0;
	for (const group of $milestoneGroups) {
		if (group.milestones) {
			for (const milestone of group.milestones) {
				await getNewExpectedAge(milestone.id);
			}
		}
		calculateProgress += delta;
	}
	calculateProgress = 100;
}

async function saveNewExpectedAges() {
	const total = $milestoneGroups.length;
	const delta = 1.0 / total;
	saveProgress = 0;
	for (const group of $milestoneGroups) {
		if (group.milestones) {
			for (const milestone of group.milestones) {
				milestone.expected_age_months = expectedAges[milestone.id].expected_age;
				const { data, error } = await updateMilestone({ body: milestone });
				if (error) {
					console.log(error);
					return;
				}
			}
		}
		saveProgress += delta;
	}
	saveProgress = 100;
	await refreshMilestoneGroups();
	console.log(saveProgress);
}
</script>

<Card size="xl" class="m-5">
    {#if milestoneGroups && i18n.locale}
        <div class="grid grid-cols-2 justify-items-stretch">
            <div class="grid grid-rows-2">
                <Button class="btn-primary" onclick={getNewExpectedAges}>
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
                {#each $milestoneGroups as milestoneGroup (milestoneGroup.id)}
                    {@const groupTitle = milestoneGroup.text[i18n.locale].title}
                    {#each milestoneGroup.milestones as milestone (milestone.id)}
                        {@const milestoneTitle = `${groupTitle} / ${milestone.text[i18n.locale].title}`}
                        {@const newExpectedAge = expectedAges?.[milestone.id]?.expected_age ?? '-'}
                        <TableBodyRow>
                            <TableBodyCell>{milestoneTitle}</TableBodyCell>
                            <TableBodyCell>{milestone.expected_age_months}</TableBodyCell>
                            <TableBodyCell>{newExpectedAge}</TableBodyCell>
                            <Button class="m-2" disabled={!expectedAges?.[milestone.id]}
                                    onclick={() => {currentMilestoneId = milestone.id; currentTitle = `${milestoneTitle} ${i18n.tr.admin.newExpectedAge}: ${newExpectedAge}m`; showMilestoneExpectedAgeModal = true;}}>{i18n.tr.admin.viewData}</Button>
                        </TableBodyRow>
                    {/each}
                {/each}
            </TableBody>
        </Table>
    {/if}
</Card>

{#key currentMilestoneId}
    <Modal title={currentTitle} bind:open={showMilestoneExpectedAgeModal} size="lg" outsideclose>
        {#if currentMilestoneId}
            <PlotScoreAge scores={expectedAges?.[currentMilestoneId].scores}/>
        {/if}
    </Modal>
{/key}
