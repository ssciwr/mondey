<svelte:options runes={true}/>

<script lang="ts">
import { download, generateCsv, mkConfig } from "export-to-csv";
import saveAs from "file-saver";
import {
	Button,
	Label,
	Modal,
	MultiSelect,
	type SelectOptionType,
	Spinner,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import { onMount } from "svelte";
import CancelButton from "#lib/components/Admin/CancelButton.svelte";
import PlotLines from "#lib/components/DataDisplay/PlotLines.svelte";
import { i18n } from "#lib/i18n.svelte.ts";
import { translationIds } from "#lib/translations.ts";
import { type PlotData } from "#lib/util.ts";
import {
	type ResearchStage,
	type WorkerError,
	type WorkerFullData,
	type WorkerFullDataRequest,
	type WorkerInit,
	type WorkerInitializeRequest,
	type WorkerProcessDataRequest,
	type WorkerProgress,
	WorkerRequestTypes,
	WorkerTypes,
	type WorkerUpdate,
	researchStages,
} from "./utilTypes";

// Web Worker for data processing
let worker: Worker;
let load_state = $state<"loading" | "ready" | "failed" | "cancelled">(
	"loading",
);
let initialized = $derived(load_state === "ready");
// Failing to process the loaded data for a selection or download does not need a reload.
let processing_error = $state(false);
let loading_stage = $state<ResearchStage>("checkingAccess");
let loading_completed = $derived(researchStages.indexOf(loading_stage));
// Existing server translations may not yet contain the new progress strings.
let research_text = $derived({
	...translationIds.researcher,
	...i18n.tr.researcher,
});

// State for spinner component
let is_loading = false;
let show_spinner: boolean = $state(false);
let show_spinner_timeout_id: number;

let is_downloading: boolean = $state(false);

// Data states (use raw state for performance as these are never mutated, only reassigned)
let json_data = $state.raw([] as any[]);
let plot_data = $state.raw({} as PlotData);
let milestone_ids = $state.raw([] as SelectOptionType<string>[]);
let milestone_ids_inv = $state.raw({} as Record<string, string>);
let columns = $state.raw([] as SelectOptionType<string>[]);
let columns_inv = $state.raw({} as Record<string, string>);

// Selection states
let selected_milestones = $state([] as string[]);
let selected_columns = $state([] as string[]);

let selected_milestone_names = $derived(
	selected_milestones.map((k) => {
		return milestone_ids_inv?.[k] ?? k;
	}),
);
let selected_column_names = $derived(
	selected_columns.map((k) => {
		return columns_inv?.[k] ?? k;
	}),
);

let downloadAllHandler: (() => void) | null = null;

function invert_select_option_array(arr: SelectOptionType<string>[]) {
	return arr.reduce(
		(obj, item) => Object.assign(obj, { [item.value]: item.name }),
		{} as Record<string, string>,
	);
}

function createWorker(): Worker {
	let worker = new Worker(new URL("./dataWorker.ts", import.meta.url), {
		type: "module",
	});

	// Handle messages from worker
	worker.onmessage = (
		event: MessageEvent<
			WorkerUpdate | WorkerInit | WorkerFullData | WorkerProgress | WorkerError
		>,
	) => {
		const response = event.data;
		if (response.type === WorkerTypes.PROGRESS) {
			loading_stage = response.stage;
			return;
		}
		if (response.type === WorkerTypes.ERROR) {
			if (response.requestType === WorkerRequestTypes.INITIALIZE) {
				handleWorkerError();
			} else {
				handleProcessingError();
			}
			return;
		}
		stop_spinner();
		if (response.type === WorkerTypes.INIT) {
			load_state = "ready";
			columns = response.columns;
			columns_inv = invert_select_option_array(columns);
			milestone_ids = response.milestone_ids;
			milestone_ids_inv = invert_select_option_array(milestone_ids);
		} else if (response.type === WorkerTypes.UPDATE) {
			json_data = response.json_data;
			plot_data = response.plot_data;
		} else if (response.type === WorkerTypes.FULL_DATA) {
			is_downloading = true;
			const blob = new Blob([response.csv_data], {
				type: "text/csv;charset=utf-8;",
			});
			saveAs(blob, `mondey_all_${new Date().toISOString().replace(/T.*/, "")}`);
			is_downloading = false;
		}
	};
	worker.onerror = handleWorkerError;
	worker.onmessageerror = handleWorkerError;

	const message: WorkerInitializeRequest = {
		requestType: WorkerRequestTypes.INITIALIZE,
		locale: i18n.locale,
	};
	worker.postMessage(message);

	return worker;
}

function destroyWorker(worker: Worker) {
	worker.terminate();
}

function handleWorkerError() {
	load_state = "failed";
	is_downloading = false;
	stop_spinner();
}

function handleProcessingError() {
	processing_error = true;
	json_data = [];
	plot_data = {} as PlotData;
	is_downloading = false;
	stop_spinner();
}

function cancelLoad() {
	destroyWorker(worker);
	load_state = "cancelled";
}

function retryLoad() {
	destroyWorker(worker);
	load_state = "loading";
	loading_stage = "checkingAccess";
	worker = createWorker();
}

onMount(() => {
	worker = createWorker();

	downloadAllHandler = () => {
		if (!worker) return;

		const message: WorkerFullDataRequest = {
			requestType: WorkerRequestTypes.FULL_DATA,
		};
		worker.postMessage(message);
	};

	return () => {
		window.clearTimeout(show_spinner_timeout_id);
		destroyWorker(worker);
	};
});

function start_spinner() {
	is_loading = true;
	const delay_ms = 100;
	// only display the spinner if we have to wait more than delay_ms
	show_spinner_timeout_id = window.setTimeout(() => {
		if (is_loading) {
			show_spinner = true;
		}
	}, delay_ms);
}

function stop_spinner() {
	window.clearTimeout(show_spinner_timeout_id);
	is_loading = false;
	show_spinner = false;
}

// Ask worker to update the data when selected milestone or group-by columns change
$effect(() => {
	if (!initialized) return;

	const message: WorkerProcessDataRequest = {
		requestType: WorkerRequestTypes.PROCESS_DATA,
		selected_milestones: $state.snapshot(selected_milestones),
		selected_columns: $state.snapshot(selected_columns),
	};
	processing_error = false;
	worker.postMessage(message);
	start_spinner();
});

function downloadCSV() {
	if (!json_data || json_data.length === 0) {
		console.log("downloadCSV clicked but no data to download");
		return;
	}
	is_downloading = true;
	const csvConfig = mkConfig({
		useKeysAsHeaders: true,
		filename: `${["mondey", new Date().toISOString().replace(/T.*/, "")].concat(selected_milestone_names).concat(selected_column_names).join("-")}`,
		quoteStrings: true,
	});
	const csv = generateCsv(csvConfig)(json_data);
	download(csvConfig)(csv);
	is_downloading = false;
}

function handleDownloadAll() {
	if (downloadAllHandler) {
		processing_error = false;
		is_downloading = true;
		downloadAllHandler();
	}
}

let headers = $derived.by(() => {
	if (!json_data || json_data.length === 0) {
		return [];
	}
	return Object.keys(json_data[0]);
});
</script>

<Modal open={load_state === "loading"} title={research_text.loadingResearchData}
    aria-label={research_text.loadingResearchData} size="md" permanent outsideclose={false}>
    <div role="status" aria-live="polite" class="space-y-2" data-testid="researchLoadProgress">
        <p id="researchLoadingStage">{research_text[loading_stage]}</p>
        <progress class="w-full h-3" max={researchStages.length} value={loading_completed}
            aria-label={research_text.loadingResearchData} aria-describedby="researchLoadingStage"></progress>
        <p class="text-sm">{loading_completed} / {researchStages.length} {research_text.loadingSteps}</p>
    </div>
    {#snippet footer()}
        <CancelButton onclick={cancelLoad} />
    {/snippet}
</Modal>

<div class="w-full grow">

    <div class="flex flex-col items-stretch m-2">
        <h4>{research_text.researchData}</h4>
        {#if load_state === "failed" || load_state === "cancelled"}
            <div role="alert" class="my-4" data-testid="researchLoadError">
                <p>{load_state === "cancelled" ? research_text.loadCancelled : research_text.error}</p>
                <Button class="mt-2" onclick={retryLoad}>{research_text.retry}</Button>
            </div>
        {:else if initialized && milestone_ids.length === 0}
            <p role="status" class="my-4">{research_text.noData}</p>
        {/if}
        <Button class="mt-9 mb-3" disabled={!initialized || !columns || columns.length === 0 || is_downloading} onclick={handleDownloadAll} data-testid="downloadAllResearchData">{research_text.downloadAll}</Button>
        {#if is_downloading}
            <div class="text-center">
                <Spinner class="mt-5" /> <span class="tertiary">{research_text.downloadingAllResearchData}</span>
            </div>
        {/if}
    </div>
    <hr class="border-gray-200" />

    <div class="flex flex-col items-stretch m-2">
        <h4>{research_text.dataPlotsHeading}</h4>
        <div class="m-2 grow">
            <Label id="selectMilestoneLabel">{research_text.milestones}</Label>
            <MultiSelect bind:value={selected_milestones} class="mt-2" items={milestone_ids}
                         disabled={!initialized}
                         placeholder={research_text.milestones}
                         aria-labelledby="selectMilestoneLabel" data-testid="selectMilestone"/>
        </div>
        <div class="m-2 grow">
            <Label id="selectGroupbyLabel">{research_text.groupbyOptional}</Label>
            <MultiSelect bind:value={selected_columns} class="mt-2" items={columns} placeholder={research_text.groupbyOptional}
                         disabled={!initialized}
                         aria-labelledby="selectGroupbyLabel" data-testid="selectGroupby"/>
        </div>
        <Button class="mt-9 mb-3" onclick={downloadCSV} data-testid="researchDownloadCSV" disabled={!initialized || !json_data || json_data.length === 0}>{research_text.downloadAsCsv}</Button>
    </div>
    {#if processing_error}
        <p role="alert" class="m-2" data-testid="researchProcessingError">{research_text.error}</p>
    {/if}
    <!-- Loading indicator -->
    {#if show_spinner}
        <div class="flex justify-center items-center h-32">
            <Spinner size="8" />
        </div>
    {:else if initialized && json_data && json_data.length > 0}
        <!-- Plot -->
        {#key plot_data}
            <div class="text-center text-2xl font-bold tracking-tight text-gray-700 dark:text-white" data-testid="researchPlotTitle">{selected_milestone_names.join(", ")} {selected_column_names.join("-")}</div>
            <div class="m-2 p-2" data-testid="researchPlotLines">
                <PlotLines {plot_data} />
            </div>
        {/key}
        <!-- Data table -->
        <Table data-testid="researchTable">
            <TableHead>
                {#each headers as header}
                    <TableHeadCell>{columns_inv?.[header] ?? header}</TableHeadCell>
                {/each}
            </TableHead>
            <TableBody>
                {#each json_data as row}
                    <TableBodyRow>
                        {#each headers as header}
                            <TableBodyCell>
                                {row?.[header]}
                            </TableBodyCell>
                        {/each}
                    </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
    {/if}
</div>
