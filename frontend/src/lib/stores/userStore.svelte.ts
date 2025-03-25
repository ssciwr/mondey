import type {
	Body_auth_cookie_login_auth_login_post,
	UserRead,
} from "$lib/client";
import {
	authCookieLogin,
	authCookieLogout,
	usersCurrentUser,
} from "$lib/client/services.gen";

function createUser() {
	let currentUser = $state(null as null | UserRead);

	return {
		login: async (
			loginData: Body_auth_cookie_login_auth_login_post,
		): Promise<any> => {
			const response = await authCookieLogin({ body: loginData });
			console.log("login response: ", response);
			return response;
		},
		logout: async (): Promise<any> => {
			const response = await authCookieLogout();
			if (response.error) {
				console.log(
					"Error during logout: ",
					response.response.status,
					response.error.detail,
				);
			} else {
				console.log("Successful logout of user ");
				currentUser = null;
			}
			return response;
		},
		load: async (): Promise<void> => {
			const { data, error } = await usersCurrentUser();

			if (error || data === undefined) {
				currentUser = null;

				console.log("Failed to get current User");
			} else {
				currentUser = data as UserRead;
			}
		},
		get data() {
			return currentUser;
		},
		get id() {
			return currentUser?.id;
		},
		get isAdmin() {
			return currentUser?.is_superuser;
		},
		get isResearcher() {
			return currentUser?.is_researcher;
		},
		get isTestAccount() {
			return (
				currentUser?.email !== undefined &&
				currentUser?.email?.indexOf("tester@testaccount.com") !== -1
			);
		},
		set data(user: UserRead | null) {
			currentUser = user;
		},
	};
}

const user = createUser();

export { user };
