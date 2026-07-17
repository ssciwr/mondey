<svelte:options runes={true}/>

<script lang="ts">
import {
	getMilestoneAnswerSessions,
	getResearchGroups,
	getUsers,
	importCsvData,
} from "$lib/client/sdk.gen";
import type { MilestoneAnswerSession } from "$lib/client/types.gen";
import AnswerSessionAnalysisModal from "$lib/components/Admin/AnswerSessionAnalysisModal.svelte";
import RecalculateStatsModal from "$lib/components/Admin/RecalculateStatsModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import {
	Alert,
	Button,
	Card,
	Checkbox,
	Label,
	Modal,
	Select,
	type SelectOptionType,
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
let stats_out_of_date = $state(false);

// CSV Import related states
let dataFile = $state(null as File | null);
let labelsFile = $state(null as File | null);
let useResearchCode = $state(false);
let researchCode = $state("");
let researchCodeOptions = $state([] as SelectOptionType<string>[]);
let dataFileInputRef = $state(null as HTMLInputElement | null);
let labelsFileInputRef = $state(null as HTMLInputElement | null);
let isUploading = $state(false);
let importResult = $state({
	status: "",
	message: "",
	error: false,
	childrenImported: 0,
});
let showImportResult = $state(false);
let successfulImport = $state(false);
let canImport = $derived(
	isCsvFile(dataFile) &&
		isCsvFile(labelsFile) &&
		(!useResearchCode || Boolean(researchCode)) &&
		!isUploading,
);

async function onStatsRecalculated() {
	stats_out_of_date = false;
	await refreshMilestoneAnswerSessions();
}

async function refreshMilestoneAnswerSessions() {
	const { data, error } = await getMilestoneAnswerSessions();
	if (error || !data) {
		console.log(error);
	} else {
		answer_sessions = data;
	}
}

async function refreshResearchGroups() {
	const [researchGroupsResponse, usersResponse] = await Promise.all([
		getResearchGroups(),
		getUsers(),
	]);
	if (
		researchGroupsResponse.error ||
		!researchGroupsResponse.data ||
		usersResponse.error ||
		!usersResponse.data
	) {
		console.log(researchGroupsResponse.error || usersResponse.error);
		return;
	}
	const researcherEmails = new Map(
		usersResponse.data
			.filter((user) => user.is_researcher && user.research_group_id > 0)
			.map((user) => [user.research_group_id, user.email]),
	);
	researchCodeOptions = researchGroupsResponse.data.map(({ id }) => {
		const email = researcherEmails.get(id);
		return {
			value: String(id),
			name: email ? `${id} (${email})` : String(id),
		};
	});
}

async function answerSessionAnalysisModalCallback() {
	stats_out_of_date = true;
	await refreshMilestoneAnswerSessions();
}

function isCsvFile(file: File | null): file is File {
	return file?.name.toLowerCase().endsWith(".csv") ?? false;
}

function selectedCsvFile(event: Event): File | null {
	const input = event.currentTarget as HTMLInputElement;
	const file = input.files?.[0] ?? null;
	if (!isCsvFile(file)) {
		input.value = "";
		return null;
	}
	return file;
}

function handleDataFileChange(event: Event) {
	dataFile = selectedCsvFile(event);
}

function handleLabelsFileChange(event: Event) {
	labelsFile = selectedCsvFile(event);
}

async function handleImport() {
	if (!canImport || !dataFile || !labelsFile) return;

	isUploading = true;
	showImportResult = false;

	try {
		const { data, error } = await importCsvData({
			body: {
				additional_data_file: dataFile,
				labels_file: labelsFile,
				research_group_id:
					useResearchCode && researchCode ? Number(researchCode) : undefined,
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
			useResearchCode = false;
			researchCode = "";
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
	if (dataFileInputRef) dataFileInputRef.value = "";
	if (labelsFileInputRef) labelsFileInputRef.value = "";
	dataFile = null;
	labelsFile = null;
	useResearchCode = false;
	researchCode = "";
}

function boolToStr(bool: boolean): string {
	return bool ? i18n.tr.admin.yes : i18n.tr.admin.no;
}

function isSuspicious(state: string): boolean {
	return state === "suspicious" || state === "admin_suspicious";
}

onMount(async () => {
	await Promise.all([
		refreshMilestoneAnswerSessions(),
		refreshResearchGroups(),
	]);
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
                                disabled={isUploading}
                                onclick={() => dataFileInputRef?.click()}
                        >
                            <FileImportSolid />
                            {dataFile ? dataFile.name : 'Choose Data File'}
                        </Button>
                        <input
                                type="file"
                                accept=".csv"
                                bind:this={dataFileInputRef}
                                onchange={handleDataFileChange}
                                disabled={isUploading}
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
                                disabled={isUploading}
                                onclick={() => labelsFileInputRef?.click()}
                        >
                            <FileImportSolid />
                            {labelsFile ? labelsFile.name : 'Choose Labels File'}
                        </Button>
                        <input
                                type="file"
                                accept=".csv"
                                bind:this={labelsFileInputRef}
                                onchange={handleLabelsFileChange}
                                disabled={isUploading}
                                data-testid="labels-csv-file-input"
                                style="display: none;"
                        />
                        {#if labelsFile}
                            <CheckCircleOutline class="text-green-500" />
                        {/if}
                    </div>
                </div>

                <div>
                    <Checkbox
                        bind:checked={useResearchCode}
                        disabled={researchCodeOptions.length === 0}
                        onchange={() => { if (!useResearchCode) researchCode = ''; }}
                    >
                        {i18n.tr.registration.researchCode}
                    </Checkbox>
                    <Label class="mt-2 block">
                        <Select
                            items={researchCodeOptions}
                            bind:value={researchCode}
                            disabled={!useResearchCode}
                            placeholder={i18n.tr.registration.selectPlaceholder}
                            data-testid="import-research-code-select"
                        />
                    </Label>
                </div>

                <Button
                    class="btn btn-primary"
                    onclick={handleImport}
                    disabled={!canImport}
                    data-testid="import-data-button"
                >
                    <FileImportSolid class="me-2 h-5 w-5" />
                    {i18n.tr.admin.importData}
                </Button>

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
    <Button onclick={() => {show_update_stats_modal = true;}} data-testid="fullStatsUpdate">
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

<RecalculateStatsModal bind:open={show_update_stats_modal} oncompleted={onStatsRecalculated}/>
