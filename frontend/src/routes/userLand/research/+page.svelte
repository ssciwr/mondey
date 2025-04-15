<svelte:options runes={true}/>

<script lang="ts">
import { getResearchDataCsv } from "$lib/client";
import PlotLines from "$lib/components/DataDisplay/PlotLines.svelte";
import { i18n } from "$lib/i18n.svelte";
import { type PlotData } from "$lib/util";
import { download, generateCsv, mkConfig } from "export-to-csv";
import {
	Button,
	Card,
	Label,
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
import type { WorkerInit, WorkerRequest, WorkerUpdate } from "./dataWorker";

// Web Worker for data processing
let worker: Worker;

// State for spinner component
let is_loading = true;
let show_spinner: boolean = $state(true);
let show_spinner_timeout_id: number;
let downloading_all: boolean = $state(false);

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
	worker.onmessage = (event: MessageEvent<WorkerUpdate | WorkerInit>) => {
		const response = event.data;
		stop_spinner();
		if (response.type === "init") {
			columns = response.columns;
			columns_inv = invert_select_option_array(columns);
			milestone_ids = response.milestone_ids;
			milestone_ids_inv = invert_select_option_array(milestone_ids);
		} else if (response.type === "update") {
			json_data = response.json_data;
			plot_data = response.plot_data;
		}
	};

	return worker;
}

function destroyWorker(worker: Worker) {
	worker.terminate();
}

onMount(() => {
	worker = createWorker();

	return () => {
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
	const message: WorkerRequest = {
		selected_milestones: $state.snapshot(selected_milestones),
		selected_columns: $state.snapshot(selected_columns),
	};
	worker.postMessage(message);
	start_spinner();
});

function downloadCurrentDataAsCSV() {
	if (!json_data || json_data.length === 0) {
		console.log("downloadCurrentDataAsCSV clicked but no data to download");
		return;
	}
	const csvConfig = mkConfig({
		useKeysAsHeaders: true,
		filename: `${["mondey", new Date().toISOString().replace(/T.*/, "")].concat(selected_milestone_names).concat(selected_column_names).join("-")}`,
		quoteStrings: true,
	});
	const csv = generateCsv(csvConfig)(json_data);
	download(csvConfig)(csv);
}

async function downloadAllResearchData() {
	try {
		is_loading = true;
		downloading_all = true;

		const response = await getResearchDataCsv();

		const blob = new Blob([response.data], { type: "text/csv" });

		const url = window.URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `mondey-research-all-${new Date().toISOString().slice(0, 10)}.csv`;
		document.body.appendChild(a);
		a.click();

		// Clean up
		window.URL.revokeObjectURL(url);
		document.body.removeChild(a);
	} catch (error) {
		console.error("Error downloading research data:", error);
		alert(i18n.tr.researcher.error || "Error downloading data");
	} finally {
		downloading_all = false;
		is_loading = false;
	}
}

let headers = $derived.by(() => {
	if (!json_data || json_data.length === 0) {
		return [];
	}
	return Object.keys(json_data[0]);
});
</script>

<div class="w-full grow">
    <Card style="display: block">
        <h1>{i18n.tr.researcher.researchData}</h1>
        <Button class="btn-secondary" disabled={downloading_all}
                 on:click={downloadAllResearchData}
                 data-testid="downloadAllResearchData">{i18n.tr.researcher.downloadAll}</Button>
        <span class="tertiary">{milestone_ids.length} {i18n.tr.researcher.milestones} </span>
    </Card>
<div class="flex flex-col items-stretch m-2">
    <div class="m-2 grow">
        <Label> {i18n.tr.researcher.milestones}
            <MultiSelect bind:value={selected_milestones} class="mt-2" items={milestone_ids}
                         placeholder={i18n.tr.researcher.milestones}
                         data-testid="selectMilestone"/>
        </Label>
    </div>
    <div class="m-2 grow">
        <Label> {i18n.tr.researcher.groupbyOptional}
            <MultiSelect bind:value={selected_columns} class="mt-2" items={columns} placeholder={i18n.tr.researcher.groupbyOptional} data-testid="selectGroupby"/>
        </Label>
    </div>
    <Button class="mt-9 mb-3" onclick={downloadCurrentDataAsCSV} data-testid="researchdownloadCurrentDataAsCSV">{i18n.tr.researcher.downloadAsCsv}</Button>
</div>
    <!-- Loading indicator -->
    {#if show_spinner}
        <div class="flex justify-center items-center h-32">
            <Spinner size="8" />
        </div>
    {:else if json_data && json_data.length > 0}
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
