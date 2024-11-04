<svelte:options runes={true} />

<script lang="ts">
import {
	getChildQuestions,
	getCurrentChildAnswers,
	updateCurrentChildAnswers,
} from "$lib/client";
import {
	type ChildAnswerPublic,
	type GetChildQuestionsResponse,
} from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading } from "flowbite-svelte";
import { _, locale } from "svelte-i18n";

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
let questionnaire: GetChildQuestionsResponse = $state(
	[] as GetChildQuestionsResponse,
);
let answers: { [k: string]: ChildAnswerPublic } = $state({});
let disableEdit: boolean = $state(false);
let alertMessage: string = $state($_("childData.alertMessageMissing"));
let showAlert = $state(false);
let promise = $state(setup());

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

	// get current child
	console.log("current child: ", $currentChild);

	if ($currentChild !== null) {
		// get existing answers
		console.log(
			"input for backend function: ",
			`/users/children-answers/${$currentChild}/`,
		);
		let currentAnswers = await getCurrentChildAnswers({
			path: {
				child_id: $currentChild,
			},
		});

		console.log("questionnaire: ", questionnaire);
		console.log("currentAnswers: ", currentAnswers.data);

		if (currentAnswers?.error || currentAnswers.data === undefined) {
			console.log(
				"Error when getting current answers for child: ",
				currentAnswers.error.detail,
			);

			showAlert = true;
			alertMessage = $_("childData.alertMessageError");
		} else {
			answers = Object.fromEntries(
				currentAnswers.data.map((existing_answer: ChildAnswerPublic) => [
					existing_answer.question_id,
					existing_answer as ChildAnswerPublic,
				]),
			);

			console.log("answers initial: ", answers);

			disableEdit = true;
		}
	}
	// add nonexisting answers
	questionnaire.forEach((question) => {
		console.log("question: ", question, "condition: ", question.id in answers);
		if (!(question.id in answers)) {
			console.log(" adding default question");
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
	console.log("questionnaire: ", questionnaire);
	console.log("answers: ", answers);
	return { questionnaire: questionnaire, answers: answers };
}

async function submitData(): Promise<void> {
	const response = await updateCurrentChildAnswers({
		body: Object.values(answers),
		path: {
			child_id: $currentChild,
		},
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
		console.log("submission of child data successful.");
		disableEdit = true;
	}
}
</script>

<Breadcrumbs data={breadcrumbdata} />
{#await promise}
	<p>{$_("childData.loadingMessage")}</p>
{:then { questionnaire, answers }}
	{#if showAlert}
		<AlertMessage
			title={$_("childData.alertMessageTitle")}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{:else}
		<div
			class="container m-2 mx-auto w-full border border-gray-200 pb-4 md:rounded-t-lg dark:border-gray-700"
		>
			<Card class="container m-1 mx-auto w-full max-w-xl">
				<Heading
					tag="h3"
					class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
					>{$_("childData.newChildLabel")}</Heading
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

				<form
					class="m-1 mx-auto w-full flex-col space-y-6"
					onsubmit={preventDefault(submitData)}
				>
					{#each questionnaire as element, i}
						{console.log(" question: ", element)}
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
							items={element.text[$locale].options_json === ""
								? undefined
								: JSON.parse(
										element.text[$locale].options_json,
									)}
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
	{/if}
{:catch error}
	<AlertMessage
		title={$_("childData.alertMessageTitle")}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
