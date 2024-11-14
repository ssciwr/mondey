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
		},
		get data() {
			return childdata;
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
