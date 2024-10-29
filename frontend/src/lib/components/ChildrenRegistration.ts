import { Input, MultiSelect, Select, Textarea } from "flowbite-svelte";

import Fileupload from "$lib/components/DataInput/Fileupload.svelte";
import RadioList from "$lib/components/DataInput/RadioList.svelte";

import {
	type ChildData,
	children,
	createDummyCurrent,
	createDummySummary,
	generateChildID,
} from "$lib/stores/childrenStore";
import { users } from "$lib/stores/userStore";

/**
 * Here the data is defined that tells the DataInput Component how to set up the necessary components for giving data about children.
 * This might have to go into the backend at some point, such that the admins can change which data should be given about children.
 * Would then be replaced with a fetch? Ideally the language id would be outside of it or the backend produes this kind of structure.
 */
const data = [
	{
		component: Input,
		value: null,
		props: {
			type: "text",

			label: "Name",
			placeholder: "Bitte eintragen",
			key: "name",
			required: true,
		},
	},
	{
		component: Input,
		value: null,
		props: {
			type: "date",

			label: "Geburtsdatum",
			placeholder: "Bitte eintragen",
			key: "dateOfBirth",
			required: true,
		},
	},
	{
		component: RadioList,
		value: null,
		additionalValue: null,
		props: {
			label: "Frühgeburt",
			items: ["nein", "0-2 Monate", "2-4 Monate", "4-6 Monate", "Anderes"].map(
				(v) => {
					return { label: String(v), value: v };
				},
			),
			placeholder: "Bitte auswählen",
			key: "bornEarly",
			required: true,
			unique: true,
			textTrigger: "Anderes",
			selected: [false, false, false, false],
		},
	},
	{
		component: RadioList,
		value: null,
		additionalValue: null,
		props: {
			label: "Geschlecht",
			items: ["männlich", "weiblich"].map((v) => {
				return { label: String(v), value: v };
			}),
			placeholder: "Bitte auswählen",
			key: "gender",
			required: true,
			unique: true,
			selected: [false, false],
		},
	},
	{
		component: MultiSelect,
		value: [],
		additionalValue: null,
		props: {
			label: "Nationalität",
			items: ["Andere", "Deutschland", "Grossbritannien", "USA", "China"].map(
				(v) => {
					return { name: String(v), value: v };
				},
			),
			placeholder: "Bitte auswählen",
			key: "nationality",
			required: true,
			textTrigger: "Andere",
		},
	},
	{
		component: MultiSelect,
		value: [],
		additionalValue: null,
		props: {
			label: "Sprache",
			items: [
				"Andere",
				"Deutsch",
				"Englisch (UK)",
				"Englisch (Us)",
				"Mandarin",
				"Arabisch",
			].map((v) => {
				return { name: String(v), value: v };
			}),
			placeholder: "Bitte auswählen",
			key: "language",
			required: true,
			textTrigger: "Andere",
		},
	},
	{
		component: Select,
		value: null,
		additionalValue: null,
		props: {
			label: "Verhältnis zum Kind",
			key: "relationship",
			items: [
				"Anderes",
				"Kind",
				"Enkelkind",
				"Neffe/Nichte",
				"Pflegekind",
				"Adoptivkind",
				"Betreuung extern",
				"Betreuung zu Hause",
			].map((v) => {
				return { name: String(v), value: v };
			}),
			placeholder: "Bitte auswählen",
			required: true,
			textTrigger: "Anderes",
		},
	},
	{
		component: MultiSelect,
		value: [],
		additionalValue: null,
		props: {
			label: "Entwicklungsauffälligkeiten",
			items: [
				"keine",
				"Hörprobleme",
				"Fehlsichtigkeit",
				"Sprachfehler",
				"Andere",
			].map((v) => {
				return { name: String(v), value: v };
			}),
			placeholder: "Bitte auswählen",
			key: "developmentalIssues",
			required: true,
			textTrigger: "Andere",
		},
	},
	{
		component: Textarea,
		value: null,
		props: {
			label: "Anmerkungen",
			placeholder: "Weitere Bemerkungen",
			key: "remarks",
			required: false,
		},
	},
	{
		component: Fileupload,
		value: null,
		props: {
			label: "Foto",
			placeholder: "Bitte wählen sie ein Bild aus falls gewünscht",
			key: "image",
			required: false,
			accept: ["png", "jpg", "svg", "webp"],
		},
	},
];

export function getData() {
	return data;
}

/**
 * README: Below is code that emulates backend behavior. This needs to be successively be replaced as the backend matures
 */

// get data from the users store on mount. This will not be used later and should be replaced with a fetch
export async function setUpOnMount() {
	await children.load();
	await users.load();

	const loggedInUser = await users.fetch("loggedIn");

	if (!children.get()[loggedInUser as string]) {
		await children.addUser(loggedInUser as string);
	}
}

// subscribe to childrenStore. This will not be used anymore later and should be replaced with a fetch
export function setUpDynamic(): unknown {
	return children.subscribe((_) => {
		children.save();
	});
}

// once the setUp* is gone, this can go too.
export async function tearDown(unsubscribe: unknown): Promise<void> {
	await children.save();
	await unsubscribe();
}

// input verification.
export function buildDataToSend(data: any[]): ChildData {
	return data.reduce((dict: any, curr) => {
		dict[curr.props.key] = curr.value;

		if (curr.additionalValue !== null) {
			dict[curr.props.key + "_additional"] = curr.additionalValue;
		}
		return dict;
	}, {});
}

export function buildRequired(data: any[]) {
	const required = {};

	data.forEach((item) => {
		required[item.props.key as string] = item.props.required;
	});

	return required;
}

export function buildMissingValues(childData: any, required: any): boolean[] {
	return Object.keys(childData).map((key) => {
		return childData[key] && required[key] ? false : true;
	});
}

export async function verifyInput(
	childData: ChildData,
	required: any,
): Promise<boolean> {
	const test = Object.entries(childData).every((kv) =>
		required[kv[0]]
			? kv[1] !== undefined && kv[1] !== null && kv[1] !== ""
			: true,
	);

	return test;
}

export async function submitData(data: any[]): Promise<void> {
	const childData = buildDataToSend(data);
	const userID = await users.getLoggedIn();

	// use showAlert flag as indicator for correct input

	const childID = generateChildID(childData.name);
	await children.addChildData(userID, childID, childData);
	await children.addChildObservation(userID, childID, {
		user: userID,
		id: childID,
		summary: await createDummySummary(),
		current: await createDummyCurrent(),
	});

	await children.save();
}
