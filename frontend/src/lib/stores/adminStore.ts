import type {
	ChildQuestionAdmin,
	MilestoneGroupAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";
import { type Writable, writable } from "svelte/store";

export const milestoneGroups: Writable<Array<MilestoneGroupAdmin>> = writable(
	[],
);

export const userQuestions: Writable<Array<UserQuestionAdmin>> = writable([]);
export const childQuestions: Writable<Array<ChildQuestionAdmin>> = writable([]);
