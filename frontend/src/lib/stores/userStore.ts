import { authCookieLogin, usersCurrentUser } from "$lib/client/services.gen";
import type { UserRead } from "$lib/client/types.gen";
import { writable } from "svelte/store";

import type { Body_auth_cookie_login_auth_login_post } from "$lib/client/types.gen";

async function hash(input: string): Promise<string> {
	const encoder = new TextEncoder();
	const data = encoder.encode(input);
	const hashArray = Array.from(
		new Uint8Array(await crypto.subtle.digest("SHA-256", data)),
	);
	const hash = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
	return hash;
}

const currentUser = writable(null as null | UserRead);

async function login(loginData: Body_auth_cookie_login_auth_login_post) {
	const response = await authCookieLogin({ body: loginData });
	if (response.error) {
		return response.error?.detail as string;
	} else {
		return "";
	}
}

async function refreshUser() {
	const { data, error } = await usersCurrentUser();

	if (error || data === undefined) {
		currentUser.set(null);

		console.log("Failed to get current User");
	} else {
		currentUser.set(data as UserRead);
	}
}

export { currentUser, hash, login, refreshUser };
