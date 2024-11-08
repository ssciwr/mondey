<script>
// @ts-nocheck
import { base } from "$app/paths";

import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";

export let getStarted = "";

export let items = [
	{
		header: "Was ist Mondey?",
		summary:
			"Mondey ist ein wissentschaftlich geprüftes Programm zure Dokumentation der Entwicklung von Kindern bis 6 Jahren.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "Wozu ist Mondey gut?",
		summary:
			"Anhand ihrer Bewertungen der Fähigkeiten des Kindes erhalten sie Feedback zum Entwicklungsstand des Kindes und können so frühzeitig Fördermaßnahmen einleiten. Dies folgt einem übersichtlichen Ampelsystem.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "Was umfasst Mondey?",
		summary:
			"Mondey umfasst unterschiedliche Entwicklungsbereiche wie von Kindern im Alter von 0 bis 6 Jahren. Dazu gehören unter anderem Grob-und feinmotorik, Wahrnehmung, Denkne, Sprache und Soziale Beziehungen.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "Wie funktioniert Mondey?",
		summary:
			"Sie bewerten wie gut das Kind bestimmte Alltagshandlungen durchführen kann mit Hilfe einer Liste von Fragen.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "Wo fange ich an?",
		summary:
			"Um zu beginnen, müssen sie sich registrieren und ein Profil für ihr Kind anlegen.",
		href: getStarted,
		button: "Los geht´s",
	},
	{
		header: "dummy?",
		summary:
			"Lorem, ipsum dolor sit amet consectetur adipisicing elit. Impedit repellendus distinctio facilis! Voluptas corrupti recusandae sapiente doloribus voluptatem fugiat ducimus.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "dummy?",
		summary:
			"Lorem, ipsum dolor sit amet consectetur adipisicing elit. Impedit repellendus distinctio facilis! Voluptas corrupti recusandae sapiente doloribus voluptatem fugiat ducimus.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
	{
		header: "dummy?",
		summary:
			"Lorem, ipsum dolor sit amet consectetur adipisicing elit. Impedit repellendus distinctio facilis! Voluptas corrupti recusandae sapiente doloribus voluptatem fugiat ducimus.",
		href: `${base}/info`,
		button: "Mehr Info",
	},
];

const props = {};
</script>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
	componentProps={props}
/>
