import { BasicStore } from "$lib/stores/basicStore";
// types. Create some interfaces to define the structure of the content and make clear what will be expected from API calls
interface MilestoneDef {
	name: string;
	items: string[];
	label: string;
}

interface ContentNode {
	milestones: MilestoneDef[];
	description: string;
	last: string | null;
	next: string | null;
}

interface ContentList {
	[name: string]: ContentNode;
}

class ContentStore extends BasicStore<ContentList> {
	static _instance: ContentStore;

	constructor(name = "content") {
		if (ContentStore._instance) {
			throw new Error(
				"Singleton classes cannot be instantiated more than once.",
			);
		} else {
			super(name, "content");
			ContentStore._instance = this;
		}
	}
}

/**
 * Create some dummy data to test the store
 */
async function createDummyData() {
	const dummySurveys = {
		surveyA: {
			description: "This is the first survey called A",
			milestones: [
				{
					name: "Standing up",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child stand up from sitting or crawling around and how readily is it able to do so",
				},
				{
					name: "Gripping a pen the right way",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child hold a pen or pencil and how coordinated can it use it",
				},
				{
					name: "Talking in full sentences",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well articulated is the child in its speech and how well can it express itself",
				},
			],
			last: null,
			next: "surveyB",
		},
		surveyB: {
			description: "This is another survey called B",
			milestones: [
				{
					name: "Standing up",
					label:
						"How well can the child hold a pen or pencil and how coordinated can it use it",
					items: ["not at all", "to some extend", "mostly", "reliably"],
				},
				{
					name: "Gripping a pen the right way",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child hold a pen or pencil and how coordinated can it use it",
				},
				{
					name: "Talking in full sentences",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well articulated is the child in its speech and how well can it express itself",
				},
				{
					name: "Counting to 10",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 10 and how well does it understand numbers within that range",
				},
			],
			last: "surveyA",
			next: "surveyC",
		},
		surveyC: {
			description: "This is another survey called C",
			milestones: [
				{
					name: "Solving a shape-sorting toy",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label: "How well can the child solve a shape-sorting toy",
				},
				{
					name: "Counting to 10",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 10 and how well does it understand numbers within that range",
				},
			],
			last: "surveyB",
			next: "surveyD",
		},
		surveyD: {
			description: "This is another survey called D",
			milestones: [
				{
					name: "Solving a shape-sorting toy",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label: "How well can the child solve a shape-sorting toy",
				},
				{
					name: "Counting to 10",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 10 and how well does it understand numbers within that range",
				},
				{
					name: "Counting to 20",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 20 and how well does it understand numbers within that range",
				},
			],
			last: "surveyC",
			next: null,
		},
		surveyE: {
			description: "This is another survey called E",
			milestones: [
				{
					name: "Solving a shape-sorting toy",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label: "How well can the child solve a shape-sorting toy",
				},
				{
					name: "Counting to 10",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 10 and how well does it understand numbers within that range",
				},
				{
					name: "Counting to 20",
					items: ["not at all", "to some extend", "mostly", "reliably"],
					label:
						"How well can the child count to 20 and how well does it understand numbers within that range",
				},
			],
			last: "surveyC",
			next: null,
		},
	};

	return dummySurveys;
}

const content = new ContentStore();

export {
	content,
	ContentStore,
	createDummyData,
	type ContentList,
	type ContentNode,
	type MilestoneDef,
};
