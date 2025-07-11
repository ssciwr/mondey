<svelte:options runes={true}/>

<script lang="ts">
import {
	adminUpdateStats,
	getMilestoneAnswerSessions,
	importCsvData,
} from "$lib/client/sdk.gen";
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
	CheckCircleOutline,
	CloseOutline,
	ExclamationCircleOutline,
	FileImportSolid,
	RefreshOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

let answer_sessions = $state([] as Array<MilestoneAnswerSession>);
let current_answer_session_id = $state(null as null | number);
let show_analysis_modal = $state(false);
let show_suspicious_only = $state(true);
let show_completed_only = $state(true);
let show_update_stats_modal = $state(false);
let update_stats_result = $state("");
let stats_out_of_date = $state(false);

// CSV Import related states
let dataFile = $state(null as File | null);
let labelsFile = $state(null as File | null);
let dataFileInputRef = $state(null);
let labelsFileInputRef = $state(null);
let isUploading = $state(false);
let showConfirmImportModal = $state(false);
let importResult = $state({
	status: "",
	message: "",
	error: false,
	childrenImported: 0,
});
let showImportResult = $state(false);
let successfulImport = $state(false);

async function doStatsUpdate() {
	show_update_stats_modal = true;
	update_stats_result = "";
	const { data, error } = await adminUpdateStats();
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

function handleDataFileChange(event) {
	const target = event.target;
	const files = target.files;
	if (files && files.length > 0) {
		dataFile = files[0];
		checkIfBothFilesUploaded();
	}
}

function handleLabelsFileChange(event) {
	const target = event.target;
	const files = target.files;
	if (files && files.length > 0) {
		labelsFile = files[0];
		checkIfBothFilesUploaded();
	}
}

function checkIfBothFilesUploaded() {
	if (dataFile && labelsFile) {
		showConfirmImportModal = true;
	}
}

async function handleImportConfirm() {
	if (!dataFile || !labelsFile) return;

	showConfirmImportModal = false;
	isUploading = true;
	showImportResult = false;

	const formData = new FormData();
	formData.append("additional_data_file", dataFile);
	formData.append("labels_file", labelsFile);

	try {
		const { data, error } = await importCsvData({
			body: {
				additional_data_file: dataFile,
				labels_file: labelsFile,
			},
		});

		if (error) {
			console.error(error);
			importResult = {
				status: "error",
				message: error.message || i18n.tr.admin.importFailed,
				error: true,
				childrenImported: 0,
			};
			cancelImport();
		} else if (data?.children_imported === 0) {
			importResult = {
				status: "error",
				message: i18n.tr.admin.emptyImport,
				error: true,
				childrenImported: 0,
			};
			cancelImport();
		} else {
			importResult = {
				status: "success",
				message: i18n.tr.admin.importSuccessful,
				error: false,
				childrenImported: data?.children_imported || 0,
			};
			// Reset file inputs
			if (dataFileInputRef) dataFileInputRef.value = "";
			if (labelsFileInputRef) labelsFileInputRef.value = "";
			dataFile = null;
			labelsFile = null;
			successfulImport = true;
			// Refresh data as it might have changed
			stats_out_of_date = true;
			await refreshMilestoneAnswerSessions();
		}
	} catch (e) {
		console.error(e);
		importResult = {
			status: "error",
			message: e.message || i18n.tr.admin.importFailed,
			error: true,
			childrenImported: 0,
		};
		cancelImport();
		console.log("Cancelled import..");
	} finally {
		isUploading = false;
		showImportResult = true;
	}
}

function cancelImport() {
	showConfirmImportModal = false;
	if (dataFileInputRef) dataFileInputRef.value = "";
	if (labelsFileInputRef) labelsFileInputRef.value = "";
	dataFile = null;
	labelsFile = null;
}

function boolToStr(bool: boolean): string {
	return bool ? i18n.tr.admin.yes : i18n.tr.admin.no;
}

function isSuspicious(state: string): boolean {
	return state === "suspicious" || state === "admin_suspicious";
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
        {#if successfulImport}
            <Alert color="green">
                <CheckCircleOutline class="inline" />&nbsp;
                {#if importResult.childrenImported > 0}
                    {importResult.childrenImported} {i18n.tr.admin.importSuccessfulChildren}
                {:else}
                    {i18n.tr.admin.importSuccessful}
                {/if}
            </Alert>
        {:else}
            <div class="space-y-4">
                <p>{i18n.tr.admin.selectFileToImport}</p>

                <!-- Data File Upload -->
                <div>
                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Data CSV File
                    </label>
                    <div class="flex items-center space-x-2">
                        <Button
                                class="btn btn-primary"
                                disabled={isUploading || dataFile !== null}
                                onclick={() => dataFileInputRef?.click()}
                        >
                            <FileImportSolid />
                            {dataFile ? dataFile.name : 'Choose Data File'}
                        </Button>
                        <input
                                type="file"
                                accept=".csv"
                                bind:this={dataFileInputRef}
                                on:change={handleDataFileChange}
                                disabled={isUploading || dataFile !== null}
                                data-testid="data-csv-file-input"
                                style="display: none;"
                        />
                        {#if dataFile}
                            <CheckCircleOutline class="text-green-500" />
                        {/if}
                    </div>
                </div>

                <!-- Labels File Upload -->
                <div>
                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Labels CSV File
                    </label>
                    <div class="flex items-center space-x-2">
                        <Button
                                class="btn btn-primary"
                                disabled={isUploading || labelsFile !== null}
                                onclick={() => labelsFileInputRef?.click()}
                        >
                            <FileImportSolid />
                            {labelsFile ? labelsFile.name : 'Choose Labels File'}
                        </Button>
                        <input
                                type="file"
                                accept=".csv"
                                bind:this={labelsFileInputRef}
                                on:change={handleLabelsFileChange}
                                disabled={isUploading || labelsFile !== null}
                                data-testid="labels-csv-file-input"
                                style="display: none;"
                        />
                        {#if labelsFile}
                            <CheckCircleOutline class="text-green-500" />
                        {/if}
                    </div>
                </div>

                {#if (dataFile && !labelsFile) || (!dataFile && labelsFile)}
                    <Alert color="yellow">
                        <ExclamationCircleOutline class="inline" />&nbsp;{i18n.tr.admin.needToUploadBothFiles}
                    </Alert>
                {/if}
            </div>
        {/if}

        {#if isUploading}
            <div class="flex items-center space-x-2">
                <Spinner size="6" class="text-blue-600"/>
                <span>{i18n.tr.admin.uploading}</span>
            </div>
        {/if}

        {#if showImportResult && importResult.error}
            <div>
                <Alert color="red" dismissable>
                    {i18n.tr.admin.importFailed}
                </Alert>
            </div>
        {/if}
    </div>
</Card>

<Card class="m-5 w-full" size="xl">
<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
    {i18n.tr.admin.data}
</h3>
{#if stats_out_of_date}
    <Alert color="red">{i18n.tr.admin.statisticsNeedUpdating}</Alert>
{/if}
<div class="grid grid-cols-2 justify-items-stretch my-2">
    <Button onclick={() => {doStatsUpdate()}} data-testid="fullStatsUpdate">
        <RefreshOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.recalculateAllStatistics}
    </Button>
</div>
{i18n.tr.admin.suspiciousSessionNote}
<Checkbox bind:checked={show_suspicious_only} class="my-2">
    {i18n.tr.admin.showSuspiciousOnly}
</Checkbox>
<Checkbox bind:checked={show_completed_only} class="my-2">
    {i18n.tr.admin.showCompletedOnly}
</Checkbox>
<div class="overflow-x-scroll overflow-y-scroll">
    <Table class="w-max max-h-[600px]">
        <TableHead>
            <TableHeadCell>Id</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.date}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.completed}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.includedInStatistics}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.suspicious}</TableHeadCell>
            <TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each answer_sessions as answer_session (answer_session.id)}
                {#if (!show_suspicious_only || isSuspicious(answer_session.suspicious_state)) && (!show_completed_only || answer_session.completed)}
                    <TableBodyRow color={isSuspicious(answer_session.suspicious_state) ? 'red' : 'default'}>
                        <TableBodyCell>
                            {answer_session.id}
                        </TableBodyCell>
                        <TableBodyCell>
                            {new Date(answer_session.created_at).toLocaleDateString(i18n.locale)}
                        </TableBodyCell>
                        <TableBodyCell>
                            {boolToStr(answer_session.completed)}
                        </TableBodyCell>
                        <TableBodyCell>
                            {boolToStr(answer_session.included_in_statistics)}
                        </TableBodyCell>
                        <TableBodyCell>
                            {answer_session.suspicious_state}
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
            {i18n.tr.admin.confirmImport}
            <br />
            Data: {dataFile?.name || 'No file'}
            <br />
            Labels: {labelsFile?.name || 'No file'}
        </h3>
        <Button color="blue" class="me-2" onclick={handleImportConfirm} data-testid="confirm-import">
            {i18n.tr.admin.yes}
        </Button>
        <Button color="alternative" onclick={cancelImport}>{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
