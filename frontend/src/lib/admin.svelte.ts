import { milestoneGroups, userQuestions } from '$lib/stores/adminStore';
import {
	authCookieLogin,
	getMilestoneGroupsAdmin,
	getUserQuestionsAdmin,
	usersCurrentUser
} from '$lib/client/services.gen';
import type {
	GetLanguagesResponse,
	MilestoneGroupAdmin,
	UserQuestionAdmin,
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
			console.log(loginData);
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
	const { data, error } = await getMilestoneGroupsAdmin();
	if (error || data == undefined) {
		console.log('Failed to get MilestoneGroups');
		milestoneGroups.set([]);
	} else {
		milestoneGroups.set(data);
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
