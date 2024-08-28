import { get, writable } from 'svelte/store';

// type interfaces
interface PersonalData {
	yearofbirth: number;
	gender: string;
	profession: string;
	education: string;
	workinghours: string;
	householdincome: string;
}

interface ScientistData extends PersonalData {
	project: string;
}

interface AdminData extends PersonalData {
	admintoken: string;
}

interface UserData {
	role: string;
	email: string;
	name: string;
	token: string;
	password: string;
	data: PersonalData | ScientistData | AdminData;
}

interface UserList {
	[key: string]: UserData;
}

// Initial user data
const userlist: UserList = {};

const users = writable(userlist);

// functions to add and delete users
async function addUser(userToken: string, userData: UserData) {
	users.update((userlist) => {
		if (userToken in userlist) {
			throw new Error('User with this token already exists');
		} else {
			userData['token'] = userToken;
			userlist[userToken] = userData;
		}
		return userlist;
	});
}

async function removeUser(userToken: string) {
	users.update((userlist) => {
		if (userToken in userlist) {
			delete userlist[userToken];
		} else {
			throw new Error('User with this token does not exist');
		}
		return userlist;
	});
}

async function fetchUser(userToken: string) {
	if (!(userToken in userlist)) {
		throw new Error('User with this token does not exist');
	} else {
		const userdata = get(users);
		return userdata[userToken];
	}
}

async function createDummyUser() {
	await addUser('dummy', {
		role: 'admin',
		email: 'dummy@nothing.com',
		name: 'dummy',
		token: 'whatever',
		password: '123',
		data: {
			yearofbirth: 1990,
			gender: 'male',
			profession: 'student',
			education: 'bachelor',
			workinghours: 'fulltime',
			householdincome: '35000-40000'
		}
	});
}

export { addUser, createDummyUser, fetchUser, removeUser, users, type UserData, type UserList };
