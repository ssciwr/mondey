import type { SelectOptionType } from "flowbite-svelte";
import type { PlotData } from "#lib/util.ts";

// Here to avoid circular import / SSR importing client / webworker code (appears as "self" error)

export enum WorkerRequestTypes {
	INITIALIZE = "requestInitialize",
	PROCESS_DATA = "requestProcessData",
	FULL_DATA = "requestFullData",
}

export enum WorkerTypes {
	INIT = "init",
	FULL_DATA = "fullData",
	UPDATE = "update",
	PROGRESS = "progress",
	ERROR = "error",
}

export const researchStages = [
	"checkingAccess",
	"answerSessions",
	"milestoneAnswers",
	"childAges",
	"userAnswers",
	"childAnswers",
	"researchGroups",
	"assembling",
	"transferring",
	"loadingNames",
	"preparing",
] as const;

export type ResearchStage = (typeof researchStages)[number];

export type WorkerProgress = {
	type: WorkerTypes.PROGRESS;
	stage: ResearchStage;
};

export type WorkerError = {
	type: WorkerTypes.ERROR;
	requestType: WorkerRequestTypes;
};

// Message types for worker communication
export type WorkerInitializeRequest = {
	requestType: WorkerRequestTypes.INITIALIZE;
	locale: string;
};

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
	csv_data: string;
};
