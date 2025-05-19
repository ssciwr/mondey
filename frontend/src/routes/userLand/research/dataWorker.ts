import type { GetResearchNamesResponse } from "$lib/client";
import { client } from "$lib/client/client.gen";
import { getResearchData, getResearchNames } from "$lib/client/sdk.gen";
import type { PlotData } from "$lib/util";
import { DataFrame, concat, toCSV, toJSON } from "danfojs";
import type { SelectOptionType } from "flowbite-svelte";
import {
	type WorkerFullData,
	type WorkerFullDataRequest,
	type WorkerInit,
	type WorkerProcessDataRequest,
	WorkerRequestTypes,
	WorkerTypes,
	type WorkerUpdate,
} from "./utilTypes";

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
	const message: WorkerInit = {
		type: WorkerTypes.INIT,
		milestone_ids: milestone_ids,
		columns: columns,
	};
	self.postMessage(message);
}

const get_raw_data = () => {
	// Create a mapping object for easier lookups
	if (df_in === null) {
		return new DataFrame();
	}
	const columnMapping: Record<string, string> = {};

	columns.forEach((item) => {
		columnMapping[item.value] = item.name.toString();
	});

	milestone_ids.forEach((item) => {
		columnMapping[item.value] = item.name.toString();
	});

	return df_in.rename(columnMapping);
};

// construct dataframe of answers for selected milestones grouped by selected columns
function get_df(selected_milestones: string[], selected_columns: string[]) {
	if (df_in === null || df_in.size === 0 || selected_milestones.length === 0) {
		return new DataFrame();
	}
	const df_list: DataFrame[] = [];
	for (const selected_milestone of selected_milestones) {
		df_list.push(
			df_in
				.loc({
					columns: ["child_age", selected_milestone].concat(selected_columns),
				})
				.dropNa()
				.rename({ [selected_milestone]: "answer" }),
		);
	}

	// Remove the empty columns/milestones
	const valid_df_list = df_list.filter((df) => df.size > 0);

	const concatenated = concat({ dfList: valid_df_list, axis: 0 }) as DataFrame;

	const grp = concatenated.groupby(["child_age"].concat(selected_columns));

	const df = grp.col(["answer"]).mean();
	if (df.size === 0) {
		return new DataFrame();
	}
	df.addColumn("answer_std", grp.col(["answer"]).std().column("answer_std"), {
		inplace: true,
	});
	df.addColumn(
		"answer_count",
		grp.col(["answer"]).count().column("answer_count"),
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
	selected_milestones: string[],
	selected_columns: string[],
) {
	if (!df_in || df_in.size === 0) {
		return;
	}
	const df = get_df(selected_milestones, selected_columns);
	const message: WorkerUpdate = {
		type: WorkerTypes.UPDATE,
		json_data: get_json_data(df),
		plot_data: get_plot_data(df, selected_columns),
	};
	self.postMessage(message);
}

function retrieve_all_data() {
	if (!df_in || df_in.size === 0) {
		return;
	}
	const df = get_raw_data();
	// using \t as seperator causes issues - some answers have columns. This protects against it
	// since danfojs version supports sep but not quoting args. And sep = \t will be ignored by users device, even if
	// we hint it with delimiter=tab in the file type, in my case at least it still used "," as a seperator too,
	const csvVersionOfData = toCSV(
		df.applyMap((val) =>
			val !== null && val !== undefined ? `"${val}"` : val,
		),
	);

	const message: WorkerFullData = {
		type: WorkerTypes.FULL_DATA,
		csv_data: csvVersionOfData,
	};
	self.postMessage(message);
}

self.onmessage = (
	event: MessageEvent<WorkerProcessDataRequest | WorkerFullDataRequest>,
) => {
	if (event.data.requestType === WorkerRequestTypes.PROCESS_DATA) {
		const { selected_milestones, selected_columns } = event.data;
		update_data(selected_milestones, selected_columns);
	} else if (event.data.requestType === WorkerRequestTypes.FULL_DATA) {
		retrieve_all_data();
	} else {
		console.warn("Request Type not matched for dataWorker message.");
	}
};

// download research data and construct initial state on creation of web worker
init();
