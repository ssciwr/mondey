import { type ChildPublic, getChild } from "$lib/client";

function createCurrentChild() {
	let currentChild: number | null = $state(null);
	let childdata: ChildPublic | null = $state(null);
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
			this.load_data();
		},
		get data() {
			return childdata;
		},
		set data(value: ChildPublic | null) {
			childdata = value;
		},

		async load_data() {
			if (currentChild === null) {
				return null;
			}

			if (childdata === null) {
				const response = await getChild({
					path: {
						child_id: currentChild,
					},
				});
				if (response.error) {
					console.log("Error during child retrieval: ", response.error);
					return null;
				} else {
					childdata = response.data;
				}
			}
		},
	};
}

export const currentChild = createCurrentChild();
