import {
	getChildQuestionsAdmin,
	getMilestoneGroupsAdmin,
	getUserQuestionsAdmin,
} from "$lib/client";
import type {
	ChildQuestionAdmin,
	MilestoneGroupAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";

function createMilestoneGroups() {
	let data = $state([] as MilestoneGroupAdmin[]);
	return {
		refresh: async (): Promise<void> => {
			const response = await getMilestoneGroupsAdmin();
			if (response.error || response.data === undefined) {
				console.log("Failed to get MilestoneGroups");
				data = [];
			} else {
				data = response.data;
			}
		},
		get data() {
			return data;
		},
	};
}

const milestoneGroups = createMilestoneGroups();

function createUserQuestions() {
	let data = $state([] as UserQuestionAdmin[]);
	return {
		refresh: async (): Promise<void> => {
			const response = await getUserQuestionsAdmin();
			if (response.error || response.data === undefined) {
				console.log("Failed to get UserQuestions");
				data = [];
			} else {
				data = response.data;
			}
		},
		get data() {
			return data;
		},
	};
}

const userQuestions = createUserQuestions();

function createChildQuestions() {
	let data = $state([] as ChildQuestionAdmin[]);
	return {
		refresh: async (): Promise<void> => {
			const response = await getChildQuestionsAdmin();
			if (response.error || response.data === undefined) {
				console.log("Failed to get ChildQuestions");
				data = [];
			} else {
				data = response.data;
			}
		},
		get data() {
			return data;
		},
	};
}

const childQuestions = createChildQuestions();

function milestoneGroupImageUrl(id: number) {
	return `${import.meta.env.VITE_MONDEY_API_URL}/static/mg/${id}.webp`;
}

export {
	milestoneGroups,
	userQuestions,
	childQuestions,
	milestoneGroupImageUrl,
};
