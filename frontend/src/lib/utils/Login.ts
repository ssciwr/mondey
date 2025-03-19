import { usersCurrentUser } from "$lib/client";
import { user } from "$lib/stores/userStore.svelte";

export async function refresh(): Promise<string> {
	const returned = await usersCurrentUser();
	if (returned.error) {
		user.data = null;
		console.log("Error getting current user: ", returned.error.detail);
		return returned.error.detail;
	}
	console.log("Successfully retrieved active user");
	if (returned.data === null || returned.data === undefined) {
		user.data = null;
		return "no user data";
	}
	user.data = returned.data;
	return "success";
}
