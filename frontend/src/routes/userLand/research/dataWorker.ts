import { type GetResearchDataResponse, getResearchData } from "$lib/client";
import type { PlotDatum } from "$lib/util";
import { DataFrame, toJSON } from "danfojs/dist/danfojs-browser/src";
import * as dfd from "danfojs/dist/danfojs-browser/src";

// Message types for worker communication
type WorkerMessage = {
	type: "processDataFully";
	selectedMilestoneId: number;
	selectedColumns: string[];
};

type WorkerResponse = {
	type: "dataProcessed";
	dfOut: any;
	jsonData: any[];
	plotData: PlotDatum[];
	columns: Array<{ value: string; name: string }>;
	milestoneIds: Array<{ value: number; name: string }>;
	firstMilestoneId: number;
};

// Process data function
function preprocessData(data: GetResearchDataResponse) {
	const df_in = new DataFrame(data);
	if (df_in.size === 0) {
		return {
			columns: [],
			milestoneIds: [],
			firstMilestoneId: 0,
			df_in,
		};
	}

	const non_question_columns = [
		"milestone_group_id",
		"milestone_id",
		"answer",
		"child_age",
		"answer_session_id",
	];

	console.log("W: Columns before: ", df_in.columns);

	const columns = df_in.columns
		.filter((c) => {
			return !non_question_columns.includes(c);
		})
		.map((k: string) => {
			return { value: k, name: k };
		});

	const milestoneIds = df_in.milestone_id.unique().values.map((k: number) => {
		return { value: k, name: `${k}` };
	});

	const firstMilestoneId = milestoneIds.length > 0 ? milestoneIds[0].value : 0;

	return {
		columns,
		milestoneIds,
		firstMilestoneId,
		df_in,
	};
}

function processData(
	df_in: DataFrame,
	selectedMilestoneId: number,
	selectedColumns: string[],
) {
	if (df_in === null || df_in.size === 0) {
		return {
			df_out: new DataFrame(),
			json_data: [],
			plot_data: [],
		};
	}

	// Process df_out
	const grp = df_in
		.loc({
			rows: df_in.milestone_id.eq(selectedMilestoneId),
		})
		.groupby(["milestone_id", "child_age"].concat(selectedColumns));

	const df_out = grp.col(["answer"]).mean();

	df_out.addColumn("answer_std", grp.col(["answer"]).std().answer_std, {
		inplace: true,
	});

	df_out.addColumn("answer_count", grp.col(["answer"]).count().answer_count, {
		inplace: true,
	});

	df_out.sortValues("child_age", { ascending: true, inplace: true });

	// Process json_data
	const json_data = dfd.toJSON(df_out) as [];

	// Process plot_data
	const plot_data: PlotDatum[] = [];

	if (df_out?.milestone_id) {
		const groupby = df_out
			.loc({
				rows: df_out.milestone_id.eq(selectedMilestoneId),
				columns: ["child_age", "answer_mean"].concat(selectedColumns),
			})
			.groupby(selectedColumns);

		const colDict = groupby.colDict as Record<
			string,
			Record<string, Array<number>>
		>;

		for (let a = 1; a < 73; ++a) {
			plot_data.push({ age: a });
		}

		for (const key in colDict) {
			for (const [index, age] of colDict[key].child_age.entries()) {
				if (age >= 1 && age <= 72) {
					plot_data[age - 1][key] = colDict[key].answer_mean[index];
				}
			}
		}
	}

	return {
		df_out,
		json_data,
		plot_data,
	};
}

const data: GetResearchDataResponse | null = null;

// Handle messages from main thread
self.onmessage = async (event: MessageEvent<WorkerMessage>) => {
	const msg = event.data; // this is not the "data data", it's the worker call

	if (msg.type === "processDataFully") {
		if (data === null) {
			const res = await getResearchData();
			if (res.error || !res.data) {
				console.error(res.error);
				console.error("W: Webworker rsearch data could not be requested...");
				return;
			}
		}
		// First preprocess the data
		const { columns, milestoneIds, firstMilestoneId, df_in } =
			preprocessData(data);
		console.log("W: Done preprocessing.");
		// Then process with the selected milestone and columns
		const milestoneId = msg.selectedMilestoneId || firstMilestoneId;
		console.log("W: Milestone ID for processing data: ", milestoneId);
		const { df_out, json_data, plot_data } = processData(
			df_in,
			milestoneId,
			msg.selectedColumns,
		);
		console.log("W: Done processing.", columns);

		// Send everything back to the main thread
		const response: WorkerResponse = {
			type: "dataProcessed",
			jsonData: json_data,
			plotData: plot_data,
			columns: columns,
			milestoneIds: milestoneIds,
			firstMilestoneId: firstMilestoneId,
		};

		if (columns.length > 0) {
			console.log("W: Completed data processing...");
			self.postMessage(response);
		}
	}
};
