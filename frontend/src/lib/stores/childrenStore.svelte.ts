import { type ChildPublic, getChild } from "#lib/client/index.ts";

function createCurrentChild() {
	let currentChild: number | null = $state(null);
	let childdata: ChildPublic | null = $state(null);
	// the child data request in progress (if any), and the id of the child it is for
	let loading: { id: number; promise: Promise<void> } | null = null;

	async function fetchChild(id: number) {
		try {
			const response = await getChild({
				path: {
					child_id: id,
				},
			});
			if (response.error) {
				console.log("Error during child retrieval: ", response.error);
			} else if (currentChild === id) {
				// ignore the response if a different child was selected in the meantime
				childdata = response.data;
			}
		} catch (error) {
			console.log("Error during child retrieval: ", error);
		}
	}

	return {
		get id() {
			return currentChild;
		},
		get name() {
			return childdata?.name;
		},
		get month() {
			return childdata?.birth_month;
		},
		get year() {
			return childdata?.birth_year;
		},
		set id(value: number | null) {
			currentChild = value;
			childdata = null;
			void this.load_data();
		},
		get data() {
			return childdata;
		},
		set data(value: ChildPublic | null) {
			childdata = value;
		},

		async load_data() {
			if (currentChild === null || childdata !== null) {
				return;
			}
			// reuse a request for the same child that is already in progress
			let request = loading;
			if (request?.id !== currentChild) {
				const newRequest = {
					id: currentChild,
					promise: fetchChild(currentChild),
				};
				void newRequest.promise.finally(() => {
					if (loading === newRequest) {
						loading = null;
					}
				});
				loading = newRequest;
				request = newRequest;
			}
			await request.promise;
		},
	};
}

export const currentChild = createCurrentChild();
