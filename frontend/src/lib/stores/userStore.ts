import { authCookieLogin, usersCurrentUser } from '$lib/client/services.gen';
import { type UserRead } from '$lib/client/types.gen';
import { BasicStore } from '$lib/stores/basicStore';
import { writable } from 'svelte/store';

import { type Body_auth_cookie_login_auth_login_post } from '$lib/client/types.gen';

interface UserData {
	name: string;
	id: string;
	role: string;
	password: string;
	[key: string]: unknown;
}

interface UserList {
	[userID: string]: UserData | string;
}

/**
 * UserStore Derived class for Users from basicStore.
 */
class UserStore extends BasicStore<UserList> {
	static _instance: UserStore;

	constructor(name: string = 'users') {
		if (UserStore._instance) {
			throw new Error('Singleton classes cannot be instantiated more than once.');
		} else {
			super(name, 'users');
			UserStore._instance = this;

			// add a flag for login status
			this.store.update((data) => {
				data['loggedIn'] = null;
				return data;
			});
		}
	}

	public async setLoggedIn(flag: string) {
		console.log('set login to: ', flag);
		this.store.update((data) => {
			data['loggedIn'] = flag;
			return data;
		});
	}

	public async getLoggedIn(): Promise<string> {
		console.log('trying to get login');
		return this.get()['loggedIn'];
	}

	public async fetchWithCredentials(
		username: string,
		userpw: string,
		role: string
	): Promise<UserData | string | undefined> {
		console.log('Fetching with credentials', username, userpw, role);

		return Object.values(this.get()).find((userdata) => {
			if (userdata && userdata !== null) {
				return userdata.name === username && userdata.password === userpw && userdata.role == role;
			} else {
				return false;
			}
		});
	}
}

const users = new UserStore();

async function createDummyUser(userStore: UserStore): Promise<void> {
	console.log('Creating dummy user');
	const h = await hash('123');
	const r = 'Beobachter';
	const name = 'dummyUser';
	await userStore.add(name + h + r, {
		id: name + h + r,
		name: name,
		role: r,
		password: h
	});
}

async function hash(input: string): string {
	const encoder = new TextEncoder();
	const data = encoder.encode(input);
	const hashArray = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', data)));
	const hash = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
	return hash;
}

const currentUser = writable(null as null | UserRead);

async function login(loginData: Body_auth_cookie_login_auth_login_post) {
	const response = await authCookieLogin({ body: loginData });
	if (response.error) {
		return response.error?.detail as string;
	} else {
		return '';
	}
}

async function refresh() {
	const { data, error } = await usersCurrentUser();
	
	if (error || data === undefined) {
		currentUser.set(null);

		console.log('Failed to get current User');
	} else {
		currentUser.set(data as UserRead);
	}
}

export { createDummyUser, currentUser, hash, login, refresh, users, type UserData, type UserList };
