import type {
	GetResearchNamesResponse,
	GetResearchNamesResponses,
} from "$lib/client";
import { client } from "$lib/client/client.gen";
import { getResearchData, getResearchNames } from "$lib/client/sdk.gen";
import type { PlotData } from "$lib/util";
import { DataFrame, toJSON } from "danfojs/dist/danfojs-browser/src";
import type { SelectOptionType } from "flowbite-svelte";

// Message types for worker communication
export type WorkerRequest = {
	selected_milestone_column: string;
	selected_columns: string[];
};

export type WorkerResponse = {
	json_data: any[];
	plot_data: PlotData;
	milestone_ids: SelectOptionType<string>[];
	columns: SelectOptionType<string>[];
};

// initial state that is constructed when web worker starts
let df_in = null as DataFrame | null;
let milestone_ids = [] as SelectOptionType<string>[];
let columns = [] as SelectOptionType<string>[];
let names = {} as GetResearchNamesResponse;

// get research data and construct initial state
async function init() {
	client.setConfig({
		baseUrl: import.meta.env.VITE_MONDEY_API_URL,
	});
	const res = await getResearchData();
	if (res.error || !res.data) {
		console.error(res.error);
		return;
	}
	df_in = new DataFrame(res.data);
	const res_names = await getResearchNames();
	if (res_names.error || !res_names.data) {
		console.error(res_names.error);
		return;
	}
	names = res_names.data;
	columns = df_in.columns
		.filter((c) => {
			return c.includes("_question_");
		})
		.map((k: string) => {
			const question_type = k.split("_")[0];
			const question_id = k.split("_").pop();
			const name = question_id
				? names?.[`${question_type}_question`]?.[question_id]
				: k;
			return { value: k, name: name };
		});
	milestone_ids = df_in.columns
		.filter((c) => {
			return c.includes("milestone_id_");
		})
		.map((column: string) => {
			const milestone_id = column.split("_").pop();
			const name = milestone_id ? names?.milestone?.[milestone_id] : column;
			return { value: column, name: name };
		});
	update_data(milestone_ids[0].value, []);
}

// construct dataframe of answers for selected milestone grouped by selected columns
function get_df(selected_milestone_column: string, selected_columns: string[]) {
	if (df_in === null || df_in.size === 0) {
		return new DataFrame();
	}
	const grp = df_in
		.loc({
			columns: ["child_age", selected_milestone_column].concat(
				selected_columns,
			),
		})
		.dropNa()
		.groupby(["child_age"].concat(selected_columns));
	const df = grp.col([selected_milestone_column]).mean();
	if (df.size === 0) {
		return new DataFrame();
	}
	df.rename(
		{ [`${selected_milestone_column}_mean`]: "answer_mean" },
		{ inplace: true },
	);
	df.addColumn(
		"answer_std",
		grp
			.col([selected_milestone_column])
			.std()
			.column(`${selected_milestone_column}_std`),
		{
			inplace: true,
		},
	);
	df.addColumn(
		"answer_count",
		grp
			.col([selected_milestone_column])
			.count()
			.column(`${selected_milestone_column}_count`),
		{
			inplace: true,
		},
	);
	df.sortValues("child_age", { ascending: true, inplace: true });
	return df;
}

// construct json data from supplied dataframe
function get_json_data(df: DataFrame) {
	if (!df || !df.child_age) {
		return [];
	}
	return toJSON(df) as [];
}

// construct plot data from supplied dataframe grouped by selected columns
function get_plot_data(df: DataFrame, selected_columns: string[]) {
	const plot_data = { keys: [], data: [] } as PlotData;
	if (!df || !df.child_age) {
		return plot_data;
	}
	const groupby = df
		.loc({
			columns: ["child_age", "answer_mean"].concat(selected_columns),
		})
		.groupby(selected_columns);
	const colDict = groupby.colDict as Record<
		string,
		Record<string, Array<number>>
	>;
	plot_data.keys = Object.keys(colDict);
	const min_child_age = 0;
	const max_child_age = 72;
	for (let a = min_child_age; a <= max_child_age; ++a) {
		plot_data.data.push({ age: a });
	}
	for (const key in colDict) {
		for (const [index, age] of colDict[key].child_age.entries()) {
			if (age >= min_child_age && age <= max_child_age) {
				// only create plot data points for ages in plotting range
				plot_data.data[age][key] = colDict[key].answer_mean[index];
			}
		}
	}
	return plot_data;
}

// send message with updated data for provided milestone and group-by columns
function update_data(
	selected_milestone_column: string,
	selected_columns: string[],
) {
	const df = get_df(selected_milestone_column, selected_columns);
	if (df_in === null || df_in.size === 0) {
		return;
	}
	const json_data = get_json_data(df);
	const plot_data = get_plot_data(df, selected_columns);
	const message: WorkerResponse = {
		json_data: json_data,
		plot_data: plot_data,
		milestone_ids: milestone_ids,
		columns: columns,
	};
	self.postMessage(message);
}

self.onmessage = (event: MessageEvent<WorkerRequest>) => {
	const { selected_milestone_column, selected_columns } = event.data;
	update_data(selected_milestone_column, selected_columns);
};

// download research data and construct initial state on creation of web worker
init();
