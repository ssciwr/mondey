import { type ChildPublic, getChild } from "$lib/client";

function createCurrentChild() {
	let currentChild: number | null = $state(null);
	let data: ChildPublic | null = $state(null);
	return {
		get id() {
			return currentChild;
		},
		set id(value: number | null) {
			currentChild = value;
		},
		async data() {
			if (currentChild === null) {
				return null;
			} else if (data === null) {
				const response = await getChild({
					path: {
						child_id: currentChild,
					},
				});
				if (response.error) {
					console.log("Error during child retrieval: ", response.error);
					return null;
				} else {
					data = response.data;
					return data;
				}
			} else {
				return data;
			}
		},
	};
}

export const currentChild = createCurrentChild();
