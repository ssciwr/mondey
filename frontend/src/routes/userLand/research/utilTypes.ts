import type { PlotData } from "$lib/util";
import type { SelectOptionType } from "flowbite-svelte";

// Here to avoid circular import / SSR importing client / webworker code (appears as "self" error)

export enum WorkerRequestTypes {
	PROCESS_DATA = "requestProcessData",
	FULL_DATA = "requestFullData",
}

export enum WorkerTypes {
	INIT = "init",
	FULL_DATA = "fullData",
	UPDATE = "update",
}

// Message types for worker communication
export type WorkerProcessDataRequest = {
	requestType: WorkerRequestTypes.PROCESS_DATA;
	selected_milestones: string[];
	selected_columns: string[];
};

export type WorkerFullDataRequest = {
	requestType: WorkerRequestTypes.FULL_DATA;
};

export type WorkerUpdate = {
	type: WorkerTypes.UPDATE;
	json_data: any[];
	plot_data: PlotData;
};

export type WorkerInit = {
	type: WorkerTypes.INIT;
	milestone_ids: SelectOptionType<string>[];
	columns: SelectOptionType<string>[];
};

export type WorkerFullData = {
	type: WorkerTypes.FULL_DATA;
	json_data: any[];
};
