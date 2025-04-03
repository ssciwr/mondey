<svelte:options runes={true}/>

<script lang="ts">
import { type GetResearchDataResponse, getResearchData } from "$lib/client";
import PlotLines from "$lib/components/DataDisplay/PlotLines.svelte";
import { i18n } from "$lib/i18n.svelte";
import { type PlotDatum } from "$lib/util";
import { DataFrame } from "danfojs/dist/danfojs-browser/src";
import { download, generateCsv, mkConfig } from "export-to-csv";
import {
	Button,
	Label,
	MultiSelect,
	Range,
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

// Web Worker for data processing
let worker: Worker;
let isLoading: string | boolean = $state(false);

// Data states
let df_out = $state(new DataFrame());
let json_data = $state([] as any[]);
let plot_data = $state([] as PlotDatum[]);

// Selection states
let selected_milestone_id = $state(1);
let milestone_ids = $state([] as SelectOptionType<number>[]);
let selected_columns = $state([] as string[]);
let columns = $state([] as SelectOptionType<string>[]);

// Create web worker on mount
onMount(() => {
	worker = new Worker(new URL("./dataWorker.ts", import.meta.url), {
		type: "module",
	});

	// Handle messages from worker
	worker.onmessage = (event) => {
		const response = event.data;

		if (response.type === "dataProcessed") {
			// Update the UI with processed data
			df_out = new DataFrame(response.dfOut);
			json_data = response.jsonData;
			plot_data = response.plotData;
			if (columns.length === 0) {
				columns = response.columns;
			}
			if (milestone_ids.length === 0) {
				milestone_ids = response.milestoneIds;
			}
			isLoading = false;
		}
	};

	// Initial data fetch
	getData();

	return () => {
		// Clean up worker when component is destroyed
		worker.terminate();
	};
});

// Track previous values to prevent infinite loops
let prev_milestone_id = $state(0);
let prev_columns = $state([] as string[]);

// Watch for changes in selection and reprocess data only when user selections change
$effect(() => {
	// Only process if values have actually changed from user interaction
	// and not from data loading
	const milestone_id_changed = selected_milestone_id !== prev_milestone_id;
	const columns_changed =
		JSON.stringify(selected_columns) !== JSON.stringify(prev_columns);

	if (milestone_id_changed || columns_changed) {
		// Update previous values
		prev_milestone_id = selected_milestone_id;
		prev_columns = [...selected_columns];

		// Process data with new selections
		processDataInWorker(selected_milestone_id, [...selected_columns]);
	}
});

function downloadCSV() {
	const csvConfig = mkConfig({
		useKeysAsHeaders: true,
		filename: `${["mondey", new Date().toISOString().replace(/T.*/, "")].concat(selected_columns).join("-")}`,
		quoteStrings: true,
	});
	const csv = generateCsv(csvConfig)(json_data as []);
	download(csvConfig)(csv);
}

// Function to send data to worker for processing
function processDataInWorker(milestoneId: number, columns: string[]) {
	if (!worker || df_out.size === 0) {
		console.log("Not processing data, as original load has not happened.");
		return false;
	}

	isLoading = `Reprocessing·data${milestoneId.toString()}...cols:·${columns.toString()}`;
	worker.postMessage({
		type: "processDataFully",
		data: null, // will be cached from original download on the worker.
		selectedMilestoneId: milestoneId,
		selectedColumns: columns,
	});
}

async function getData() {
	console.log("Loading data from API");
	try {
		isLoading = "Loading Data";
		const res = await getResearchData();
		if (res.error || !res.data) {
			console.error(res.error);
			isLoading = false;
			return;
		}

		isLoading = "Loading";
		// Send fetched data to worker for processing
		console.log("Requested worker to compute the data");
		worker.postMessage({
			type: "processDataFully",
			data: structuredClone(res.data),
			selectedMilestoneId: Number(selected_milestone_id),
			selectedColumns: [...selected_columns],
		});
	} catch (error) {
		console.error("Error fetching data:", error);
		isLoading = false;
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

    <!-- Controls -->
    <div class="flex flex-row items-stretch m-2">
        <div class="m-2">
            <Label> {i18n.tr.researcher.milestoneId}
                <Select bind:value={selected_milestone_id} class="mt-2" items={milestone_ids}
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
    {#if isLoading}
        <div class="flex justify-center items-center h-32">
            <Spinner size="8" />
        </div>
    {:else if json_data && json_data.length > 0}
        <!-- Plot -->
        {#key plot_data}
            <div class="text-center text-2xl font-bold tracking-tight text-gray-700 dark:text-white" data-testid="researchPlotTitle">
                {i18n.tr.researcher.milestone} {selected_milestone_id} {selected_columns.join("-")}
            </div>
            <div class="m-2 p-2" data-testid="researchPlotLines">
                <PlotLines scores={plot_data} />
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
