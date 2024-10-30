import { BasicStore } from "$lib/stores/basicStore";
import { get } from "svelte/store";
// README: this API is experimental and not by any means a final design

// Types: create interfaces for the elements that are stored and are expected to be returned from the 'backend' (or its mockup at the moment)
/**
 * Interface for the observation data of a child
 * @param id identifier of the child
 * @param user user identifier
 * @param summary summary of the observation: table that contains the status of the child for each survey for each date
 * @param current current status of individual milestones for the currently open survey
 */
interface ObservationData {
	id: string;
	user: string;
	summary: object;
	current: object;
}

/**
 * Interface for the data of a child
 * @param name name of the child
 * @param id identifier of the child
 * @param user user identifier
 * @param image image of the child
 * @param [key: string] further data elements
 */
interface ChildData {
	name: string;
	id: string;
	user: string;
	[key: string]: unknown;
}

/**
 *
 */
interface ChildObject {
	childData: ChildData;
	observationData: ObservationData | null;
}

/**
 *
 */
interface ChildrenList {
	[usertoken: string]: {
		[childtoken: string]: ChildObject;
	};
}

class ChildrenStore extends BasicStore<ChildrenList> {
	static _instance: ChildrenStore;

	/**
	 *
	 * @param name
	 */
	constructor(name = "children") {
		if (ChildrenStore._instance) {
			throw new Error(
				"Singleton classes cannot be instantiated more than once.",
			);
		} else {
			super(name, "children");
			ChildrenStore._instance = this;
		}
	}
	/**
	 *
	 * @param userID
	 * @returns
	 */
	public async addUser(userID: string): Promise<void> {
		return this.add(userID, {});
	}

	/**
	 *
	 * @param userID
	 */
	public async removeUser(userID: string): Promise<void> {
		this.remove(userID);
	}

	/**
	 * Add new child data to the data of a user
	 * @param usertoken User identifier to add the child to
	 * @param childtoken Child identifier to add the child to
	 * @param data data of the child to add
	 */
	public async addChildData(
		usertoken: string,
		childtoken: string,
		data: ChildData,
	) {
		// /API calls/ fetch requests could go here.

		this.store.update((childrenlist) => {
			if (!(usertoken in childrenlist)) {
				throw new Error(`User token ${usertoken} not found`);
			}

			if (childtoken in childrenlist[usertoken as keyof typeof childrenlist]) {
				throw new Error(
					`Child token ${childtoken} already exists for user token ${usertoken}`,
				);
			}

			childrenlist[usertoken][childtoken] = {
				childData: data,
				observationData: null,
			};

			return childrenlist;
		});
	}

	/**
	 *
	 * Add observation data to the data of a child
	 * @param usertoken User identifier to add the child to
	 * @param childtoken Child identifier to add observation data to
	 * @param observationData The observationdata to add
	 */
	public async addChildObservation(
		usertoken: string,
		childtoken: string,
		observationData: ObservationData,
	) {
		this.store.update((childrenlist) => {
			if (!(usertoken in childrenlist)) {
				throw new Error(`User token ${usertoken} not found`);
			}

			if (
				!(childtoken in childrenlist[usertoken as keyof typeof childrenlist])
			) {
				throw new Error(
					`Child token ${childtoken} does not exist for user token ${usertoken}`,
				);
			}

			childrenlist[usertoken as keyof typeof childrenlist][
				childtoken
			].observationData = observationData;

			return childrenlist;
		});
	}

	/**
	 * Remove a child from the data of a user
	 * @param usertoken user identifer to remove the child from
	 * @param childtoken childidentifier to remove
	 */
	public async removeChildData(usertoken: string, childtoken: string) {
		// /API calls/ fetch requests could go here.

		this.store.update((childrenlist) => {
			if (!(usertoken in childrenlist)) {
				throw new Error(`User token ${usertoken} not found`);
			}

			if (
				!(childtoken in childrenlist[usertoken as keyof typeof childrenlist])
			) {
				throw new Error(
					`Child token ${childtoken} not found for user token ${usertoken}`,
				);
			}

			delete childrenlist[usertoken as keyof typeof childrenlist][childtoken];

			return childrenlist;
		});
	}

	/**
	 * Retrieve the data of a child
	 * @param usertoken user to fetch child data from
	 * @param childtoken child identifier to fetch data from
	 * @returns ChildData of the child
	 */
	public async fetchChildData(usertoken: string, childtoken: string) {
		// /API calls/ fetch requests could go here.
		const contentData = get(this.store);

		if (!(usertoken in contentData)) {
			throw new Error("No such user in the childrenstore");
		}

		if (!(childtoken in contentData[usertoken])) {
			throw new Error(
				"No such child in the childrenstore for user " + usertoken,
			);
		}

		return contentData[usertoken][childtoken].childData;
	}

	/**
	 * Retrieve the observation data of a child
	 * @param usertoken user to fetch child observations from
	 * @param childtoken child identifier to fetch observations from
	 * @returns ObservationData of the child
	 */
	public async fetchObservationData(usertoken: string, childtoken: string) {
		// /API calls/ fetch requests could go here.
		const contentData = get(this.store);

		if (!(usertoken in contentData)) {
			throw new Error("No such user in the childrenstore");
		}

		if (!(childtoken in contentData[usertoken as keyof typeof contentData])) {
			throw new Error(
				"No such child in the childrenstore for user " + usertoken,
			);
		}

		return contentData[usertoken as keyof typeof contentData][childtoken]
			.observationData;
	}

	/**
	 * fetch all the children data of a user
	 * @param usertoken User to fetch data for
	 * @returns a list of ChildData objects for the user, sorted alphabetically by child name.
	 */
	public async fetchChildrenDataforUser(usertoken: string) {
		const contentData = get(this.store);

		if (!(usertoken in contentData)) {
			throw new Error("No such user in the childrenstore");
		}

		// sort them alphabetically
		return Object.keys(contentData[usertoken as keyof typeof contentData])
			.map((child) => {
				return contentData[usertoken as keyof typeof contentData][child]
					.childData;
			})
			.sort((a, b) => a.name.localeCompare(b.name));
	}

	/**
	 * fetch all observationdata for all children of a user
	 * @param usertoken user to fetch data for
	 * @returns A list of tuples, where the first element is the child identifier and the second element is the observation data of the child
	 */
	public async fetchObservationDataForUser(usertoken: string) {
		const contentData = get(this.store);

		if (!(usertoken in contentData)) {
			throw new Error("No such user in the childrenstore");
		}

		return Object.keys(contentData[usertoken as keyof typeof contentData]).map(
			(child) => {
				return [
					child,
					contentData[usertoken as keyof typeof contentData][child]
						.observationData,
				];
			},
		);
	}
}

/**
 * Generate a dummy child id code
 * @param childname name of the child
 * @returns child id code string made up of ascii code numbers in string form
 */
export function generateChildID(childname: string): string {
	return childname
		.split("")
		.map((char) => char.charCodeAt(0))
		.reduce((acc, num) => acc + num.toString(), "")
		.toLowerCase();
}

// --> README:
// hardcode dummy child data which later will live in the database on the server and be fetched from there via API calls
// the stuff below is therefore temporary and is an approximation of the datastructure that may be returned perhaps from the backend,
// and thus is subject to change

/**
 * helper function for generating random integers
 * @param max the maximum value of the random integer (always starts from 0)
 * @returns
 */
function getRandomInt(max: number) {
	return Math.floor(Math.random() * max);
}

/**
 * helper function for choosing a random value from a list
 * @param values list of values to choose from
 * @returns
 */
function chooseRandom(values: string[]) {
	return values[getRandomInt(values.length)];
}

/**
 *
 * @returns
 */
async function createDummySummary() {
	const values = ["good", "warn", "bad"];
	const dates = [
		"05-11-2017",
		"08-05-2016",
		"22-07-2012",
		"11-11-2020",
		"30-03-2019",
		"01-06-2022",
		"30-12-2021",
		"30-11-2021",
		"30-10-2021",
	];
	const surveys: string[] = [
		"surveyA",
		"surveyB",
		"surveyC",
		"surveyD",
		"surveyE",
	];

	interface SummaryElement {
		name: string;
		[key: string]: unknown;
	}
	const summary: SummaryElement[] = [];

	for (const s of surveys) {
		const element: SummaryElement = { name: s };

		for (const date of dates) {
			element[date] = chooseRandom(values);
		}
		summary.push(element);
	}

	return summary;
}

async function createDummyCurrent() {
	const current: { [survey: string]: { name: string; status: string }[] } = {};
	const surveys: string[] = [
		"surveyA",
		"surveyB",
		"surveyC",
		"surveyD",
		"surveyE",
	];

	const milestones = [
		"milestoneA",
		"milestoneB",
		"milestoneC",
		"milestoneD",
		"milestoneE",
	];
	const completionValues = ["done", "open", "incomplete"];

	for (const survey of surveys) {
		current[survey] = [];
		for (const milestone of milestones) {
			current[survey].push({
				name: milestone,
				status: chooseRandom(completionValues),
			});
		}
	}
	return current;
}
const children = new ChildrenStore();

export {
	children,
	ChildrenStore,
	createDummyCurrent,
	createDummySummary,
	type ChildData,
	type ChildObject,
	type ChildrenList,
	type ObservationData,
};
