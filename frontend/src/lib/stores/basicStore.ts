import { browser } from "$app/environment";
import { type Subscriber, type Writable, get, writable } from "svelte/store";

/**
 *
 */
class BasicStore<T extends Record<string, unknown>> {
	protected store: Writable<T>;
	protected key: string;
	protected name: string;

	/**
	 *
	 * @param name
	 * @param key
	 */
	constructor(name: string, key: string) {
		this.name = name;
		this.store = writable({} as T);
		this.key = key;
	}

	public get() {
		return get(this.store);
	}

	public subscribe(subscriber: Subscriber<T>): unknown {
		return this.store.subscribe(subscriber);
	}
	/**
	 *
	 * @param data
	 */
	public set(data: T): void {
		this.store.set(data);
	}

	/**
	 *
	 * @param userID
	 * @param element
	 */
	public async add(userID: string, element: unknown): Promise<void> {
		console.log(`adding ${userID}`);
		console.log(`  registered users: ${Object.keys(get(this.store))}`);
		if (userID in get(this.store)) {
			throw new Error(`User ${userID} already exist`);
		}

		this.store.update((data: T) => {
			data[userID as keyof T] = element as T[keyof T];

			return data;
		});
	}

	/**
	 *
	 * @param userID
	 * @param element
	 */
	public async update(userID: string, element: unknown): Promise<void> {
		if (!(userID in get(this.store))) {
			throw new Error(`User ${userID} doesn't exist`);
		}
		this.store.update((data) => {
			data[userID as keyof T] = element as T[keyof T];
			return data;
		});
	}

	/**
	 *
	 * @param userID
	 */
	public async remove(userID: string): Promise<void> {
		if (!(userID in get(this.store))) {
			throw new Error(`User ${userID} doesn't exist`);
		}

		this.store.update((data) => {
			delete data[userID];

			return data;
		});
	}

	/**
	 *
	 * @param userID
	 * @returns
	 */
	public fetch(userID: string): Promise<unknown> {
		const data = get(this.store);

		if (!(userID in data)) {
			throw new Error(`User ${userID} doesn't exist`);
		}
		return data[userID];
	}

	/**
	 * save the data contained int he store to localstorage
	 */
	public async save(): Promise<void> {
		if (browser) {
			localStorage.setItem(this.key, JSON.stringify(get(this.store)));
		}
	}

	/**
	 *
	 */
	public async load(): Promise<void> {
		let data = {};

		if (browser) {
			const stored = localStorage.getItem(this.key);
			data = stored ? JSON.parse(stored) : {};
		}
		this.store.set(data as T);
	}
}

export { BasicStore };
