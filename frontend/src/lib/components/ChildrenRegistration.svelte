<script lang="ts">
import { base } from "$app/paths";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import {
	buildDataToSend,
	buildMissingValues,
	buildRequired,
	getData,
	setUpDynamic,
	setUpOnMount,
	submitData,
	tearDown,
	verifyInput,
} from "$lib/components/ChildrenRegistration";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import NavigationButtons from "$lib/components/Navigation/NavigationButtons.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { Card, Heading } from "flowbite-svelte";
import { onDestroy, onMount } from "svelte";

// get data to fill in
const data = getData();

const breadcrumbdata = [
	{
		label: "Kinderübersicht",
		onclick: () => {
			activeTabChildren.update((value) => {
				return "childrenGallery";
			});
		},
	},
	{
		label: "Neues Kind registrieren",
	},
];

// use component lifecycle to make sure data is written and read persistently

onMount(setUpOnMount);

onDestroy(async () => {
	await tearDown(unsubscribe);
});

// data to display -> will later be fetched from the server
const heading = "Neues Kind registrieren";

// data
let unsubscribe: unknown = setUpDynamic();

// rerender page if missing values or showAlert changes
let missingValues = [];
$: showAlert = false;
$: showCheckMessage = true;

const buttons = [
	{
		label: "Abschließen",
		onclick: async () => {
			const childData = buildDataToSend(data);
			const required = buildRequired(data);
			const verified = await verifyInput(childData, required);
			if (verified) {
				console.log("good");
				showAlert = false;
				await submitData(data);
				activeTabChildren.update((v) => {
					return "childrenGallery";
				});
			} else {
				console.log("not good");
				missingValues = buildMissingValues(childData, required);
				showAlert = true;
			}
		},
	},
];
</script>

<div
	class="container m-2 mx-auto w-full border border-gray-200 pb-4 md:rounded-t-lg dark:border-gray-700"
>
	<Breadcrumbs data={breadcrumbdata} />
	<!-- Show big alert message when something is missing -->
	{#if showAlert}
		<AlertMessage
			title="Fehler"
			message="Bitte füllen Sie mindestens die benötigten Felder (hervorgehoben) aus."
			infopage="{base}/info"
			infotitle="Was passiert mit den Daten"
			onclick={() => {
				showAlert = false;
				missingValues = [];
			}}
		/>
	{/if}

	{#if showCheckMessage}
		<AlertMessage
			title="Bevor es weitergeht"
			message="Bitte überprüfen sie ihre eingaben nochmals genau bevor sie weiter gehen"
			infopage="{base}/info"
			infotitle="Was passiert mit den Daten?"
			onclick={() => {
				showCheckMessage = false;
			}}
		/>
	{/if}

	<!-- The actual content -->

	<Card class="container m-1 mx-auto w-full max-w-xl">
		{#if heading}
			<Heading
				tag="h3"
				class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
				>{heading}</Heading
			>
		{/if}

		<form class="m-1 mx-auto w-full flex-col space-y-6">
			{#each data as element}
				<DataInput
					component={element.component}
					bind:value={element.value}
					bind:additionalValue={element.additionalValue}
					label={element.props.label}
					properties={element.props}
					textTrigger={element.props.textTrigger}
				/>
			{/each}
		</form>
		<NavigationButtons {buttons} />
	</Card>
</div>
