import { milestoneGroups, userQuestions } from '$lib/stores/adminStore';
import {
	authCookieLogin,
	getMilestoneGroupsAdmin,
	getUserQuestionsAdmin,
	getMilestoneAgeGroups,
	createMilestoneAgeGroup,
	deleteMilestoneAgeGroup,
	usersCurrentUser,
	updateMilestoneAgeGroup
} from '$lib/client/services.gen';
import type {
	MilestoneAgeGroupPublic,
	MilestoneGroupAdmin,
	MilestoneAgeGroupCreate,
	UserRead,
	Body_auth_cookie_login_auth_login_post
} from '$lib/client/types.gen';

function AdminUser() {
	let user = $state(null as UserRead | null);
	return {
		get value(): UserRead | null {
			return user;
		},
		login: async function (loginData: Body_auth_cookie_login_auth_login_post) {
			const { data, error } = await authCookieLogin({ body: loginData });
			if (error) {
				return error?.detail as string;
			} else {
				await this.refresh();
				if (!user || !user.is_superuser) {
					return 'Admin account required';
				}
				return '';
			}
		},
		refresh: async function () {
			const { data, error } = await usersCurrentUser();
			if (error || data === undefined) {
				console.log('Failed to get current User');
				user = null;
			} else {
				user = data;
			}
		}
	};
}

export const adminUser = AdminUser();

export async function refreshMilestoneGroups() {
	console.log('refreshMilestoneGroups...');
	await milestoneAgeGroups.refresh();
	if (!milestoneAgeGroups.value) {
		return;
	}
	const groups = {} as Record<string, Array<MilestoneGroupAdmin>>;
	for (const ageGroup of milestoneAgeGroups.value) {
		const { data, error } = await getMilestoneGroupsAdmin({
			query: {
				milestone_age_group_id: ageGroup.id
			}
		});
		if (error || data == undefined) {
			console.log(`Failed to get MilestoneGroups for ${ageGroup}`);
		} else {
			groups[`${ageGroup.id}`] = data;
		}
		milestoneGroups.set(groups);
		console.log(groups);
	}
}

export function milestoneGroupImageUrl(id: number) {
	return `${import.meta.env.VITE_MONDEY_API_URL}/static/mg${id}.jpg`;
}

export async function refreshUserQuestions() {
	console.log('refreshQuestions...');
	const { data, error } = await getUserQuestionsAdmin();
	if (error || data === undefined) {
		console.log('Failed to get UserQuestions');
		userQuestions.set([]);
	} else {
		userQuestions.set(data);
	}
}

function MilestoneAgeGroups() {
	let milestoneAgeGroups = $state(null as Array<MilestoneAgeGroupPublic> | null);
	return {
		get value(): Array<MilestoneAgeGroupPublic> | null {
			return milestoneAgeGroups;
		},
		create: async function (ageGroup: MilestoneAgeGroupCreate) {
			const { data, error } = await createMilestoneAgeGroup({ body: ageGroup });
			if (error || data === undefined) {
				console.log(`Failed to create MilestoneAgeGroup ${ageGroup}`);
			} else {
				await this.refresh();
			}
		},
		save: async function (ageGroup: MilestoneAgeGroupPublic) {
			const { data, error } = await updateMilestoneAgeGroup({ body: ageGroup });
			if (error || data === undefined) {
				console.log(`Failed to save MilestoneAgeGroup ${ageGroup}`);
			} else {
				await this.refresh();
			}
		},
		delete: async function (id: number) {
			const { data, error } = await deleteMilestoneAgeGroup({
				path: {
					milestone_age_group_id: id
				}
			});
			if (error || data === undefined) {
				console.log(`Failed to delete MilestoneAgeGroup ${id}`);
			} else {
				await this.refresh();
			}
		},
		refresh: async function () {
			const { data, error } = await getMilestoneAgeGroups();
			if (error || data === undefined) {
				console.log('Failed to get MilestoneAgeGroups');
				milestoneAgeGroups = null;
			} else {
				milestoneAgeGroups = data;
			}
		}
	};
}

export const milestoneAgeGroups = MilestoneAgeGroups();
