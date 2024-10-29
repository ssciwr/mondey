import { base } from "$app/paths";
import imgJump from "$lib/assets/baby0.jpg";
import imgHead from "$lib/assets/baby2.jpg";
import { activeTabChildren } from "$lib/stores/componentStore";

export function createStyle(data: any[]) {
	return data.map((item) => {
		return {
			card: {
				class:
					"m-2 max-w-prose dark:text-white text-gray-700 hover:cursor-pointer ",
			},
			header: null,
			summary: null,
			progress: {
				labelInsideClass: "h-4 rounded-full text-xs text-center text-white",
				size: "h-4",
				divClass: `h-full rounded-full w-${100 * item.progress}`,
				color: "primary",
				completeColor: "green",
			},
		};
	});
}

export const milestoneData = [
	{
		number: 1,
		title: "Alleine von Stufe/Absatz springen",
		desc: "Kind springt mit beiden Beinen gleichzeitig hoch und überwindet im Sprung freihändig einen (kleinen) Absatz oder eine Stufe. Es kommt sicher wieder im Stand auf.",
		observation:
			"Beobachten Sie, ob das Kind spontan oder nach Aufforderung von einer Treppenstufe oder einem ähnlich hohen Absatz springt! Es sollte tatsächlich mit beiden Beinen gleichzeitig losspringen, sich nirgends festhalten und beim Landen nicht mit der Hand abfangen. Sie sollten es beim Springen auch nicht an die Hand nehmen müssen. Wurde dieses Verhalten mehrmals sicher ausgeführt, gilt der Meilenstein zuverlässig gekonnt.  Ist das Kind noch leicht unsicher, springt meist mit beiden Beinen versetzt los, oder berührt beim Landen mit der Hand den Boden, ist das Verhalten weitgehend gekonnt. Wagt es den Sprung nur, wenn man seine Hand hält und/oder führt es den Sprung noch unsauber aus, ist das Verhalten in Ansätzen gekonnt. In allen anderen Fällen gilt der Meilenstein als noch nicht gekonnt.",
		help: "Beim Treppengehen im Haus, beim Spazierengehen oder auf dem Spielplatz bieten sich vielfältige Gelegenheiten, Kinder zum Springen von einem Absatz (z.B. einem höheren Bordstein. einem Holzstamm, oder einem Stein) zu ermutigen. Machen Sie Ihrem Kind die Bewegung vor oder führen Sie sie gemeinsam mit dem Kind durch. Nehmen Sie das Kind dafür zunächst bei an die Hand. Später können sie die Hand immer lockerer mitführen und die Eigenbewegung des Kindes nur noch passiv begleiten. So kann das Kind am besten selbst herausfinden, wie es seine Arme einsetzen muss, um Schwung zu holen und beim Landen das Gleichgewicht zu finden. Ist das Springen an der Hand sicher, lösen Sie die Hand ganz und stellen Sie sich gegenüber dem Kind hin, damit es weiß, dass es im Notfall aufgefangen wird.",
		imgs: ["baby0.jpg", "baby1.jpg", "baby2.jpg"],
		answer: "Vollständig gekonnt",
	},
	{
		number: 2,
		title: "Das Köpfchen alleine heben",
		desc: "Kind liegt auf dem Bauch, hält die Arme angewinkelt neben dem Körper und hebt sein Köpfchen aus eigener Kraft so hoch, dass das Kinn nicht mehr die Auflage berührt. Diese Position kann es mehr als 3 Sekunden halten.",
		observation: "Hier kommt der Beobachtungshilfetext hin",
		help: "Hier kommt der Förderhilfetext hin",
		imgs: ["baby1.jpg"],
		answer: null,
	},
	{
		number: 3,
		title: "Den Kopf frei bewegen",
		desc: "Kind kann seinen Kopf frei halten und bewegen, wenn es z.B. auf dem Schoß sitzt. Wenn man seinen Körper ein wenig schräg hält, gleicht es diese Bewegung mit dem Kopf aus. Der Kopf wackelt kaum oder gar nicht, wenn das Kind ihn dreht.",
		observation: "Hier kommt der Beobachtungshilfetext hin",
		help: "Hier kommt der Förderhilfetext hin",
		imgs: ["baby2.jpg"],
		answer: "In Ansätzen gekonnt",
	},
	{
		number: 4,
		title: "Sich in Bauchlage mit gestreckten Armen aufstützen",
		desc: "Kind liegt auf dem Bauch. Es stützt sich mit beiden Armen gestreckt von der Unterlage ab und hebt seinen Rücken an, um den Kopf aufrecht zu halten. Schultern und Brust liegen für mehr als 3 Sekunden nicht mehr auf der Unterlage.",
		observation: "Hier kommt der Beobachtungshilfetext hin",
		help: "Hier kommt der Förderhilfetext hin",
		imgs: ["baby3.jpg"],
		answer: null,
	},
];

// this is a list of data that can be fetched by the component later.
export const surveyData: any[] = [
	{
		header: "Grobmotorik",
		summary: "something something",
		image: imgJump,
		href: `${base}/milestoneoverview`,
		progress: 0.75,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Feinmotorik",
		summary:
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt",
		image: null,
		href: `${base}/milestoneoverview`,
		progress: 1.0,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Geistige Grundfunktionen",
		summary: "something something",
		image: imgHead,
		href: `${base}/milestoneoverview`,
		progress: 1.0,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Höhere Denkfunktionen",
		summary: "something something",
		image: null,
		href: `${base}/milestoneoverview`,
		progress: 1.0,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Sprache",
		summary: "how much noise the child makes",
		image: null,
		progress: 0.5,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Soziale Entwicklung",
		summary:
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
		image: imgHead,
		progress: 0.3,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Selbstregulation",
		summary: "something something",
		image: null,
		progress: 0.6,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Emotionen",
		summary: "something something",
		image: null,
		progress: 0.9,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
	{
		header: "Vorläuferfertigkeiten Schule",
		summary:
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
		image: null,
		progress: 0.3,
		milestoneData: milestoneData,
		events: {
			onclick: (event) => {
				activeTabChildren.update((_) => {
					return "milestoneOverview";
				});
			},
		},
	},
];
