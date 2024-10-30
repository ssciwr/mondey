<svelte:options runes={true} />

<script lang="ts">
import { base } from "$app/paths";
import {
	getChildQuestions,
	getCurrentChildrenAnswers,
	updateCurrentChildrenAnswers,
} from "$lib/client";
import {
	type ChildAnswerPublic,
	type GetChildQuestionsResponse,
} from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading } from "flowbite-svelte";
import { _, locale } from "svelte-i18n";

// get data to fill in
const breadcrumbdata = [
	{
		label: $_("childData.overviewLabel"),
		onclick: () => {
			activeTabChildren.update((value) => {
				return "childrenGallery";
			});
		},
	},
	{
		label: $_("childData.newChildLabel"),
	},
];

// data to display -> will later be fetched from the server
const heading = $_("childData.newChildLabel");
let questionnaire: GetChildQuestionsResponse = $state(
	[] as GetChildQuestionsResponse,
);
let answers: { [k: string]: ChildAnswerPublic } = $state({});
let disableEdit: boolean = $state(false);
let alertMessage: string = $state($_("childData.alertMessageMissing"));
let promise = $state(setup());
let showAlert = $state(false);

async function setup(): Promise<{
	questionnaire: GetChildQuestionsResponse;
	answers: { [k: string]: ChildAnswerPublic };
}> {
	// get questions
	const questions = await getChildQuestions();
	if (questions.error || questions.data === undefined) {
		console.log("Error when getting userquestions: ", questions.error.detail);
		showAlert = true;
		alertMessage = $_("childData.alertMessageError");
	} else {
		questionnaire = questions.data as GetChildQuestionsResponse;
	}

	// get existing answers
	let currentAnswers = await getCurrentChildrenAnswers();
	if (currentAnswers?.error || currentAnswers.data === undefined) {
		console.log(
			"Error when getting current answers for child: ",
			currentAnswers.error.detail,
		);

		showAlert = true;
		alertMessage = $_("childData.alertMessageError");
	} else {
		answers = Object.fromEntries(
			currentAnswers.data.map((existing_answer) => [
				existing_answer.question_id,
				existing_answer as ChildAnswerPublic,
			]),
		);
		disableEdit = true;

		// add nonexisting answers
		questionnaire.map((question) => {
			if (!(question.id in answers)) {
				answers[question.id] = {
					question_id: question.id,
					answer: "",
					additional_answer: "",
				} as ChildAnswerPublic;

				disableEdit = false;
				showAlert = true;
				alertMessage = $_("childData.alertMessageUpdate");
			}
		});
	}

	return { questionnaire: questionnaire, answers: answers };
}

async function submitData(): Promise<void> {
	const response = await updateCurrentChildrenAnswers({
		body: Object.values(answers),
	});

	if (response.error) {
		console.log(
			"Error when sending user question answers: ",
			response.error.detail,
		);
		alertMessage = $_("childData.alertMessageError");
		showAlert = true;
	} else {
		// disable all elements to make editing a conscious choice
		disableEdit = true;
	}
}
</script>

<Breadcrumbs data={breadcrumbdata} />
{#await promise}
	<p>{$_("childData.loadingMessage")}</p>
{:then { questionnaire, answers }}
	<div
		class="container m-2 mx-auto w-full border border-gray-200 pb-4 md:rounded-t-lg dark:border-gray-700"
	>
		{#if showAlert}
			<AlertMessage
				title="Fehler"
				message="Bitte füllen Sie mindestens die benötigten Felder (hervorgehoben) aus."
				infopage="{base}/info"
				infotitle="Was passiert mit den Daten"
				onclick={() => {
					showAlert = false;
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

			<form
				class="m-1 mx-auto w-full flex-col space-y-6"
				onsubmit={preventDefault(submitData)}
			>
				{#each questionnaire as element}
					<DataInput
						component={componentTable[element.component]}
						bind:value={answers[element.id].answer}
						bind:additionalValue={answers[element.id]
							.additional_answer}
						label={element?.text[$locale].question}
						textTrigger={element.additional_option}
						required={true}
						additionalRequired={true}
						id={"input_" + String(i)}
						items={JSON.parse(element.text[$locale].options_json)}
						disabled={disableEdit}
					/>
				{/each}
				{#if disableEdit === true}
					<Button
						type="button"
						class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
						on:click={() => {
							disableEdit = false;
						}}
					>
						<div class="flex items-center justify-center">
							{$_("childData.changeData")}
						</div>
					</Button>
				{:else}
					<Button
						class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
						type="submit"
						>{$_("childData.submitButtonLabel")}</Button
					>
				{/if}
			</form>
		</Card>
	</div>
{:catch error}
	<AlertMessage
		title={$_("childData.alertMessageTitle")}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
