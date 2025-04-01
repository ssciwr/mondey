<svelte:options runes={true}/>

<script lang="ts">
import { type GetResearchDataResponse, getResearchData } from "$lib/client";
import PlotLines from "$lib/components/DataDisplay/PlotLines.svelte";
import { i18n } from "$lib/i18n.svelte";
import { type PlotDatum } from "$lib/util";
import { DataFrame, toJSON } from "danfojs/dist/danfojs-browser/src";
import { download, generateCsv, mkConfig } from "export-to-csv";
import {
	Button,
	Label,
	MultiSelect,
	Range,
	Select,
	type SelectOptionType,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import { onMount } from "svelte";

let df_in = $state(null as DataFrame | null);

let selected_milestone_id = $state(1);
let milestone_ids = $state([] as SelectOptionType<number>[]);

let selected_columns = $state([] as string[]);
let columns = $state([] as SelectOptionType<string>[]);

function downloadCSV() {
	const csvConfig = mkConfig({
		useKeysAsHeaders: true,
		filename: `${["mondey", new Date().toISOString().replace(/T.*/, "")].concat(selected_columns).join("-")}`,
		quoteStrings: true,
	});
	const csv = generateCsv(csvConfig)(toJSON(df_out) as []);
	download(csvConfig)(csv);
}

let df_out = $derived.by(() => {
	if (df_in === null || df_in.size === 0) {
		return new DataFrame();
	}
	let grp = df_in
		.loc({
			rows: df_in.milestone_id.eq(selected_milestone_id),
		})
		.groupby(["milestone_id", "child_age"].concat(selected_columns));
	let df = grp.col(["answer"]).mean();
	df.addColumn("answer_std", grp.col(["answer"]).std().answer_std, {
		inplace: true,
	});
	df.addColumn("answer_count", grp.col(["answer"]).count().answer_count, {
		inplace: true,
	});
	df.sortValues("child_age", { ascending: true, inplace: true });
	return df;
});

let json_data = $derived.by(() => {
	if (!df_out || !df_out.milestone_id) {
		return [];
	}
	return toJSON(df_out) as [];
});

let plot_data: PlotDatum[] = $derived.by(() => {
	if (!df_out || !df_out.milestone_id) {
		return [];
	}
	const groupby = df_out
		.loc({
			rows: df_out.milestone_id.eq(selected_milestone_id),
			columns: ["child_age", "answer_mean"].concat(selected_columns),
		})
		.groupby(selected_columns);
	const colDict = groupby.colDict as Record<
		string,
		Record<string, Array<number>>
	>;
	let plot_data: Array<PlotDatum> = [];
	for (let a = 1; a < 73; ++a) {
		plot_data.push({ age: a });
	}
	for (const key in colDict) {
		for (const [index, age] of colDict[key].child_age.entries()) {
			if (age < 1 || age > 72) {
				console.log(age);
			} else {
				plot_data[age - 1][key] = colDict[key].answer_mean[index];
			}
		}
	}
	return plot_data;
});
let headers = $derived.by(() => {
	if (!json_data || json_data.length === 0) {
		return [];
	}
	return Object.keys(json_data[0]);
});

function preproccessData(data: GetResearchDataResponse) {
	df_in = new DataFrame(data);
	if (df_in.size === 0) {
		columns = [];
		milestone_ids = [];
		return;
	}
	const non_question_columns = [
		"milestone_group_id",
		"milestone_id",
		"answer",
		"child_age",
		"answer_session_id",
	];
	columns = df_in.columns
		.filter((c) => {
			return !non_question_columns.includes(c);
		})
		.map((k: string) => {
			return { value: k, name: k };
		});
	milestone_ids = df_in.milestone_id.unique().values.map((k: number) => {
		return { value: k, name: `${k}` };
	});
	selected_milestone_id = milestone_ids[0].value;
}

async function getData() {
	const res = await getResearchData();
	if (res.error || !res.data) {
		console.error(res.error);
		return;
	}
	preproccessData(res.data ?? []);
}

onMount(async () => {
	await getData();
});

// <TODO>: remove this once production site has real data
let n_answer_sessions = $state(2000);
let n_milestones = $state(10);
function sample(min: number, max: number): number {
	return min + Math.floor(Math.random() * (max - min + 1));
}
function generateFakeData() {
	const data: Array<Record<string, string | number>> = [];
	let answer_session_id = 1;
	for (let i = 0; i < n_answer_sessions; ++i) {
		for (let milestone_id = 1; milestone_id <= n_milestones; ++milestone_id) {
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
	preproccessData(data);
}
// </TODO>
</script>

<div class="w-full grow">
<!-- <TODO>: remove this once production site has real data-->
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
<!-- </TODO> -->
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
{#if json_data && json_data.length > 0}
    {#key plot_data}
        <div class="text-center text-2xl font-bold tracking-tight text-gray-700 dark:text-white" data-testid="researchPlotTitle">{i18n.tr.researcher.milestone} {selected_milestone_id} {selected_columns.join("-")}</div>
        <div class="m-2 p-2" data-testid="researchPlotLines">
            <PlotLines scores={plot_data} />
        </div>
    {/key}
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
