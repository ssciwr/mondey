<svelte:options runes={true}/>

<script lang="ts">
import {
    adminUpdateStats,
    getMilestoneAnswerSessions, importCsvData,
} from "$lib/client/sdk.gen";

import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";
import type { MilestoneAnswerSession } from "$lib/client/types.gen";
import AnswerSessionAnalysisModal from "$lib/components/Admin/AnswerSessionAnalysisModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import {
	Alert,
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
	FileImportSolid,
	RefreshOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

let answer_sessions = $state([] as Array<MilestoneAnswerSession>);
let current_answer_session_id = $state(null as null | number);
let show_analysis_modal = $state(false);
let show_suspicious_only = $state(true);
let show_update_stats_modal = $state(false);
let update_stats_result = $state("");
let stats_out_of_date = $state(false);

// CSV Import related states
let csvFile = $state(null as File | null);
let fileInputRef = $state(null);
let isUploading = $state(false);
let showConfirmImportModal = $state(false);
let importResult = $state({ status: '', message: '', error: false });
let showImportResult = $state(false);

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
		stats_out_of_date = false;
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

async function answerSessionAnalysisModalCallback() {
	stats_out_of_date = true;
	await refreshMilestoneAnswerSessions();
}

function handleFileChange(event) {
    const target = event.target;
    const files = target.files;
    if (files && files.length > 0) {
        csvFile = files[0];
        showConfirmImportModal = true;
    }
}

async function handleImportConfirm() {
    if (!csvFile) return;

    showConfirmImportModal = false;
    isUploading = true;
    showImportResult = false;

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
        const { data, error } = await importCsvData({
            body: { file: csvFile },
        });

        if (error) {
            console.error(error);
            importResult = {
                status: 'error',
                message: error.message || i18n.tr.admin.importFailed,
                error: true
            };
        } else {
            importResult = {
                status: 'success',
                message: i18n.tr.admin.importSuccessful,
                error: false
            };
            // Reset file input
            if (fileInputRef) fileInputRef.value = '';
            csvFile = null;
            // Refresh data as it might have changed
            stats_out_of_date = true;
            await refreshMilestoneAnswerSessions();
        }
    } catch (e) {
        console.error(e);
        importResult = {
            status: 'error',
            message: e.message || i18n.tr.admin.importFailed,
            error: true
        };
    } finally {
        isUploading = false;
        showImportResult = true;
    }
}

function cancelImport() {
    showConfirmImportModal = false;
    if (fileInputRef) fileInputRef.value = '';
    csvFile = null;
}

onMount(async () => {
    await refreshMilestoneAnswerSessions();
});
</script>

<Card class="m-5 w-full" size="xl">
    <h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
        {i18n.tr.admin.importData}
    </h3>
    <div class="space-y-4">
        <div>
            <input
                    type="file"
                    accept=".csv"
                    bind:this={fileInputRef}
                    on:change={handleFileChange}
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    disabled={isUploading}
                    data-testid="csv-file-input"
            />
            <Button color="blue" disabled={isUploading || !csvFile}>
                <FileImportSolid />
                {i18n.tr.admin.uploadCSV}
            </Button>
        </div>

        {#if isUploading}
            <div class="flex items-center space-x-2">
                <Spinner size="6" class="text-blue-600"/>
                <span>{i18n.tr.admin.uploading}</span>
            </div>
        {/if}

        {#if showImportResult}
            <Alert color={importResult.error ? "red" : "green"} dismissable>
                {importResult.message}
            </Alert>
        {/if}
    </div>
</Card>

<Card class="m-5 w-full" size="xl">
    <h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
        {i18n.tr.admin.manageData}
    </h3>
    {#if stats_out_of_date}
        <Alert color="red">{i18n.tr.admin.statisticsNeedUpdating}</Alert>
    {/if}
    <div class="grid grid-cols-2 justify-items-stretch my-2">
        <Button class="mr-2" onclick={() => {doStatsUpdate(true)}} data-testid="incrementalStatsUpdate">
            <RefreshOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.updateStatistics}
        </Button>
        <Button onclick={() => {doStatsUpdate(false)}} data-testid="fullStatsUpdate">
            <RefreshOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.recalculateAllStatistics}
        </Button>
    </div>
    {i18n.tr.admin.suspiciousSessionNote}
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
                                callback={answerSessionAnalysisModalCallback}/>
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

<!-- Confirmation Modal for CSV Import -->
<Modal bind:open={showConfirmImportModal} size="xs" autoclose>
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {csvFile?.name ? `${i18n.tr.admin.confirmImport} "${csvFile.name}"?` : i18n.tr.admin.confirmImport}
        </h3>
        <Button color="blue" class="me-2" onclick={handleImportConfirm} data-testid="confirm-import">
            {i18n.tr.admin.yes}
        </Button>
        <Button color="alternative" onclick={cancelImport}>{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>