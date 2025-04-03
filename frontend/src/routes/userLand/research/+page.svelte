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
let isLoading = $state(false);

// Data states
let df_out = $state(new DataFrame());
let json_data = $state([] as any[]);
let plot_data = $state([] as PlotDatum[]);

// Selection states
let selected_milestone_id = $state(1);
let milestone_ids = $state([] as SelectOptionType<number>[]);
let selected_columns = $state([] as string[]);
let columns = $state([] as SelectOptionType<string>[]);

let tries = $state(0 as number);

// Create web worker on mount
onMount(() => {
	worker = new Worker(new URL("./dataWorker.ts", import.meta.url), {
		type: "module",
	});

	// Handle messages from worker
	worker.onmessage = (event) => {
		const response = event.data;

		if (response.type === "dataProcessed") {
			console.log("Data returned!", response);
			// Update the UI with processed data
			df_out = new DataFrame(response.dfOut);
			console.log("Set df_out");
			json_data = response.jsonData;
			console.log("SEt JSON");
			plot_data = response.plotData;
			console.log("Set Plot.");
			if (columns.length === 0) {
				console.log(
					"SEtting columns to: ",
					response.columns,
					" they were: ",
					columns,
				);
				columns = response.columns;
			}
			if (milestone_ids.length === 0) {
				console.log(
					"SEtting milestone IDs to: ",
					response.milestoneIds,
					"they were: ",
					milestone_ids,
				);
				milestone_ids = response.milestoneIds;
			}

			// Set initial milestone if needed
			// THis was causing infinite re-renders(!)
			/*if (selected_milestone_id <= 0 && response.firstMilestoneId > 0) {
				selected_milestone_id = response.firstMilestoneId;
			}*/

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

$inspect(
	"Inspect: ",
	selected_columns,
	"milestone ID: ",
	selected_milestone_id,
);

// Watch for changes in selection and reprocess data
$effect(() => {
	processDataInWorker(selected_milestone_id, [...selected_columns]);
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

		isLoading = "Computing";

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

// Fake data generation (remains in main thread as requested)
let n_answer_sessions = $state(2000);
let n_milestones = $state(10);

function sample(min: number, max: number): number {
	return min + Math.floor(Math.random() * (max - min + 1));
}

function generateFakeData() {
	console.log("Generating fake data");
	isLoading = "Generating Fake Data";
	const data: Array<Record<string, string | number>> = [];
	let answer_session_id = 1;

	// Get primitive values from potentially proxied state
	const sessionsCount = Number(n_answer_sessions);
	const milestonesCount = Number(n_milestones);
	const milestoneId = Number(selected_milestone_id);
	const columnsArray = [...selected_columns]; // Create a new array from the proxy

	for (let i = 0; i < sessionsCount; ++i) {
		for (
			let milestone_id = 1;
			milestone_id <= milestonesCount;
			++milestone_id
		) {
			data.push({
				milestone_group_id: 1,
				milestone_id: milestone_id,
				answer: sample(1, 4),
				child_age: sample(1, 72),
				answer_session_id: answer_session_id,
				"number of older siblings": ["0", "1", "2", "3+"][sample(0, 3)],
				"number of younger siblings": ["0", "1", "2", "3+"][sample(0, 3)],
				"early birth": ["yes", "no"][sample(0, 1)],
				"parental education": [
					"school",
					"university degree",
					"postgraduate degree",
					"other",
				][sample(0, 3)],
			});
			++answer_session_id;
		}
	}
	console.log("Data prepped...", data);

	// Send fake data to worker for processing using only primitive values
	worker.postMessage({
		type: "processDataFully",
		data: data, // This is already a plain object array
		selectedMilestoneId: milestoneId,
		selectedColumns: columnsArray,
	});
	console.log("Sent worker request to process data fully.");
}

let headers = $derived.by(() => {
	if (!json_data || json_data.length === 0) {
		return [];
	}
	return Object.keys(json_data[0]);
});
</script>

<div class="w-full grow">
    <!-- Fake data generation UI -->
    <div class="flex flex-col m-2 bg-red-300">
        Temporary FAKE data generation:
        <div class="flex flex-row items-stretch m-2">
            <div class="m-2 grow">
                <Label> {n_milestones} milestones
                    <Range min="0" max="200" bind:value={n_milestones} />
                </Label>
            </div>
            <div class="m-2 grow">
                <Label> {n_answer_sessions} answer sessions
                    <Range min="0" max="100000" bind:value={n_answer_sessions} />
                </Label>
            </div>
            <Button onclick={generateFakeData}>Generate FAKE data</Button>
        </div>
    </div>

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
            <Spinner size="8" />&nbsp;{isLoading}
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
