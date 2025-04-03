<svelte:options runes={true}/>

<script lang="ts">
import PlotLines from "$lib/components/DataDisplay/PlotLines.svelte";
import { i18n } from "$lib/i18n.svelte";
import { type PlotData } from "$lib/util";
import { download, generateCsv, mkConfig } from "export-to-csv";
import {
	Button,
	Label,
	MultiSelect,
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
import { onMount } from "svelte";
import type { WorkerRequest, WorkerResponse } from "./dataWorker";

// Web Worker for data processing
let worker: Worker;

// State for spinner component
let is_loading = true;
let show_spinner: boolean = $state(true);
let show_spinner_timeout_id: number;

// Data states (use raw state for performance as these are never mutated, only reassigned)
let json_data = $state.raw([] as any[]);
let plot_data = $state.raw({} as PlotData);
let milestone_ids = $state.raw([] as SelectOptionType<string>[]);
let columns = $state.raw([] as SelectOptionType<string>[]);

// Selection states
let selected_milestone_column = $state("");
let selected_columns = $state([] as string[]);

function createWorker(): Worker {
	let worker = new Worker(new URL("./dataWorker.ts", import.meta.url), {
		type: "module",
	});

	// Handle messages from worker
	worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
		const response = event.data;
		stop_spinner();
		// update the plot & table data
		json_data = response.json_data;
		plot_data = response.plot_data;
		// only update these if they are empty (i.e. the first time)
		if (columns.length === 0) {
			columns = response.columns;
		}
		if (milestone_ids.length === 0) {
			milestone_ids = response.milestone_ids;
		}
		if (selected_milestone_column === "") {
			selected_milestone_column = milestone_ids[0].value;
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
		selected_milestone_column: selected_milestone_column,
		selected_columns: $state.snapshot(selected_columns),
	};
	worker.postMessage(message);
	start_spinner();
});

function downloadCSV() {
	if (!json_data || json_data.length === 0) {
		console.log("downloadCSV clicked but no data to download");
		return;
	}
	const csvConfig = mkConfig({
		useKeysAsHeaders: true,
		filename: `${["mondey", new Date().toISOString().replace(/T.*/, "")].concat(selected_columns).join("-")}`,
		quoteStrings: true,
	});
	const csv = generateCsv(csvConfig)(json_data);
	download(csvConfig)(csv);
}

let headers = $derived.by(() => {
	if (!json_data || json_data.length === 0) {
		return [];
	}
	return Object.keys(json_data[0]);
});
</script>

<div class="w-full grow">
<div class="flex flex-row items-stretch m-2">
    <div class="m-2">
        <Label> {i18n.tr.researcher.milestoneId}
            <Select bind:value={selected_milestone_column} class="mt-2" items={milestone_ids}
                    placeholder={i18n.tr.researcher.milestoneId}
                    data-testid="selectMilestone"/>
        </Label>
    </div>
    <div class="m-2 grow">
        <Label> {i18n.tr.researcher.groupbyOptional}
            <MultiSelect bind:value={selected_columns} class="mt-2" items={columns} placeholder={i18n.tr.researcher.groupbyOptional} data-testid="selectGroupby"/>
        </Label>
    </div>
    <Button class="mt-9 mb-3" onclick={downloadCSV} data-testid="researchDownloadCSV">{i18n.tr.researcher.downloadAsCsv}</Button>
</div>
    <!-- Loading indicator -->
    {#if show_spinner}
        <div class="flex justify-center items-center h-32">
            <Spinner size="8" />
        </div>
    {:else if json_data && json_data.length > 0}
        <!-- Plot -->
        {#key plot_data}
            <div class="text-center text-2xl font-bold tracking-tight text-gray-700 dark:text-white" data-testid="researchPlotTitle">{i18n.tr.researcher.milestone} {selected_milestone_column.split("_").pop()} {selected_columns.join("-")}</div>
            <div class="m-2 p-2" data-testid="researchPlotLines">
                <PlotLines {plot_data} />
            </div>
        {/key}
        <!-- Data table -->
        <Table data-testid="researchTable">
            <TableHead>
                {#each headers as header}
                    <TableHeadCell>{header}</TableHeadCell>
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
