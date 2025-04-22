<svelte:options runes={true}/>

<script lang="ts">
import {
	adminUpdateStats,
	getMilestoneAnswerSessions,
} from "$lib/client/sdk.gen";
import type { MilestoneAnswerSession } from "$lib/client/types.gen";
import AnswerSessionAnalysisModal from "$lib/components/Admin/AnswerSessionAnalysisModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import {
	Button,
	Card,
	Checkbox,
	Modal,
	Spinner,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import {
	ChartPieOutline,
	CloseOutline,
	RefreshOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

let answer_sessions = $state([] as Array<MilestoneAnswerSession>);
let current_answer_session_id = $state(null as null | number);
let show_analysis_modal = $state(false);
let show_suspicious_only = $state(true);
let show_update_stats_modal = $state(false);
let update_stats_result = $state("");

async function doStatsUpdate(incremental: boolean) {
	show_update_stats_modal = true;
	update_stats_result = "";
	const { data, error } = await adminUpdateStats({
		path: {
			incremental_update: incremental,
		},
	});
	if (error || !data) {
		console.log(error);
		update_stats_result = i18n.tr.admin.error;
	} else {
		update_stats_result = data;
		await refreshMilestoneAnswerSessions();
	}
}

async function refreshMilestoneAnswerSessions() {
	const { data, error } = await getMilestoneAnswerSessions();
	if (error || !data) {
		console.log(error);
	} else {
		answer_sessions = data;
	}
}

onMount(async () => {
	await refreshMilestoneAnswerSessions();
});
</script>

<Card class="m-5 w-full" size="xl">
    <h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
        {i18n.tr.admin.data}
    </h3>
    <div class="grid grid-cols-2 justify-items-stretch my-2">
        <Button class="mr-2" onclick={() => {doStatsUpdate(true)}} data-testid="incrementalStatsUpdate">
            <RefreshOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.updateStatistics}
        </Button>
        <Button onclick={() => {doStatsUpdate(false)}} data-testid="fullStatsUpdate">
            <RefreshOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.recalculateAllStatistics}
        </Button>
    </div>
    <Checkbox bind:checked={show_suspicious_only} class="my-2">
        {i18n.tr.admin.showSuspiciousOnly}
    </Checkbox>
    <div class="overflow-x-scroll overflow-y-scroll">
        <Table class="w-max max-h-[600px]">
            <TableHead>
                <TableHeadCell>Id</TableHeadCell>
                <TableHeadCell>{i18n.tr.admin.date}</TableHeadCell>
                <TableHeadCell>{i18n.tr.admin.includedInStatistics}</TableHeadCell>
                <TableHeadCell>{i18n.tr.admin.suspicious}</TableHeadCell>
                <TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
            </TableHead>
            <TableBody>
                {#each answer_sessions as answer_session (answer_session.id)}
                    {#if !show_suspicious_only || answer_session.suspicious}
                        <TableBodyRow color={answer_session.suspicious ? 'red' : 'default'}>
                            <TableBodyCell>
                                {answer_session.id}
                            </TableBodyCell>
                            <TableBodyCell>
                                {new Date(answer_session.created_at).toLocaleDateString(i18n.locale)}
                            </TableBodyCell>
                            <TableBodyCell>
                                {answer_session.included_in_statistics ? i18n.tr.admin.yes : i18n.tr.admin.no}
                            </TableBodyCell>
                            <TableBodyCell>
                                {answer_session.suspicious ? i18n.tr.admin.yes : i18n.tr.admin.no}
                            </TableBodyCell>
                            <TableBodyCell>
                                <Button onclick={() => {if(answer_session.id) {current_answer_session_id=answer_session.id;
							show_analysis_modal=true;}}} data-testid={`analyze-${answer_session.id}`}>
                                    <ChartPieOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.analyze}</Button>
                            </TableBodyCell>
                        </TableBodyRow>
                    {/if}
                {/each}
            </TableBody>
        </Table>
    </div>
</Card>


{#key current_answer_session_id}
    <AnswerSessionAnalysisModal answer_session_id={current_answer_session_id} bind:open={show_analysis_modal}
                                callback={refreshMilestoneAnswerSessions}/>
{/key}

<Modal bind:open={show_update_stats_modal} size="md" title={i18n.tr.admin.updateStatistics}>
    {#if !update_stats_result}
        <Spinner class="me-2 h-5 w-5"/>{i18n.tr.admin.statisticsAreBeingUpdated}
    {:else}
        {update_stats_result}
    {/if}
    <svelte:fragment slot="footer">
        <Button color="alternative" onclick={()=>{show_update_stats_modal=false}} disabled={!update_stats_result}>
            <CloseOutline class="me-2 h-5 w-5" data-testid="closeUpdateStatsModal"/> {i18n.tr.admin.close}
        </Button>
    </svelte:fragment>
</Modal>
