import { children } from "$lib/stores/childrenStore";
import { activeTabChildren } from "$lib/stores/componentStore";
import { users } from "$lib/stores/userStore";

export function convertData(rawdata) {
	const data = rawdata.map((item) => {
		return {
			header: item.name,
			summary: item.info ? item.info : "",
			image: item.image,
			events: {
				onclick: (event) => {
					activeTabChildren.update((_) => {
						return "milestoneGroup";
					});
				},
			},
		};
	});

	// put in new element at the front which adds new child
	data.unshift({
		header: "Neu",
		summary: "Ein neues Kind anmelden",
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "childrenRegistration";
				});
			},
		},
	});
	return data;
}

// dynamically create the styles for individual gallery tiles based on the data.
// The 'Neu' element needs to be styled differently in particular
export function createStyle(data) {
	return data.map((item) => ({
		card:
			item.header === "Neu"
				? {
						class:
							"hover:cursor-pointer m-2 max-w-prose bg-primary-700 dark:bg-primary-600 hover:bg-primary-800 dark:hover:bg-primary-700",
						horizontal: false,
					}
				: { horizontal: false },
		header:
			item.header == "Neu"
				? {
						class:
							"mb-2 text-2xl font-bold tracking-tight text-white dark:text-white",
					}
				: null,
		summary:
			item.header == "Neu"
				? {
						class:
							"mb-3 flex font-normal leading-tight text-white dark:text-white",
					}
				: null,
		button: null,
	}));
}

export async function init(): Promise<any[]> {
	users.load();
	try {
		await children.load();
	} catch (error) {
		console.log("Error loading data: ", error);
	}

	const loggedIn = users.get()["loggedIn"];

	// Update the store with the value from localStorage
	let rawdata: unknown = [];

	try {
		rawdata = await children.fetchChildrenDataforUser(loggedIn);
	} catch (error) {
		console.log("some error occured: ", error);
	}

	return convertData(rawdata);
}
