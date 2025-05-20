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

function createAdminStore<T>(
	fetchFn: () => Promise<{ data?: T[]; error?: any }>,
	entityName: string,
) {
	let data = $state([] as T[]);
	let isLoading = $state(false);
	let error = $state(null as string | null);

	return {
		refresh: async (): Promise<void> => {
			isLoading = true;
			error = null;

			try {
				const response = await fetchFn();
				if (response.error || response.data === undefined) {
					error = `Failed to get ${entityName}: ${response.error || "Unknown error"}`;
					data = [];
				} else {
					data = response.data;
				}
			} catch (e) {
				error = `Exception while fetching ${entityName}: ${e instanceof Error ? e.message : String(e)}`;
				data = [];
			} finally {
				isLoading = false;
			}
		},
		get data() {
			return data;
		},
		get isLoading() {
			return isLoading;
		},
		get error() {
			return error;
		},
	};
}

const milestoneGroups = createAdminStore<MilestoneGroupAdmin>(
	getMilestoneGroupsAdmin,
	"MilestoneGroupAdmin",
);

const userQuestions = createAdminStore<UserQuestionAdmin>(
	getUserQuestionsAdmin,
	"UserQuestionAdmin",
);

const childQuestions = createAdminStore<ChildQuestionAdmin>(
	getChildQuestionsAdmin,
	"ChildQuestionAdmin",
);

function milestoneGroupImageUrl(id: number) {
	return `${import.meta.env.VITE_MONDEY_API_URL}/static/mg/${id}.webp`;
}

export {
	milestoneGroups,
	userQuestions,
	childQuestions,
	milestoneGroupImageUrl,
};
