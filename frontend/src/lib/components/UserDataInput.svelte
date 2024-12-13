<svelte:options runes={true} />

<script lang="ts">
import {
	getCurrentUserAnswers,
	getUserQuestions,
	updateCurrentUserAnswers,
} from "$lib/client/services.gen";
import {
	type GetUserQuestionsResponse,
	type UserAnswerPublic,
} from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { i18n } from "$lib/i18n.svelte";
import { componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading } from "flowbite-svelte";

async function submitData() {
	const response = await updateCurrentUserAnswers({
		body: Object.values(answers),
	});

	if (response.error) {
		console.log(
			"Error when sending user question answers: ",
			response.error.detail,
		);
		alertMessage = i18n.tr.userData.alertMessageError;
		showAlert = true;
	} else {
		// disable all elements to make editing a conscious choice
		disableEdit = true;
	}
}

async function setup() {
	const userQuestions = await getUserQuestions();

	// get questions
	if (userQuestions.error || userQuestions.data === undefined) {
		console.log(
			"Error when getting userquestions: ",
			userQuestions.error.detail,
		);
		showAlert = true;
		alertMessage = i18n.tr.userData.alertMessageError;
	} else {
		questionnaire = userQuestions.data;
	}
	// get current answers.
	let currentAnswers = await getCurrentUserAnswers();

	if (currentAnswers?.error || currentAnswers.data === undefined) {
		console.log(
			"Error when getting current answers for users: ",
			currentAnswers?.error?.detail,
		);

		showAlert = true;
		alertMessage = i18n.tr.userData.alertMessageError;
	} else {
		// make map of question_id => answer. Don´t rely on questions and
		// answers being aligned
		answers = Object.fromEntries(
			currentAnswers.data.map((existing_answer) => [
				existing_answer.question_id,
				existing_answer as UserAnswerPublic,
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
				} as UserAnswerPublic;

				disableEdit = false;
			}
		});
	}
	return { questionnaire: questionnaire, answers: answers };
}

let questionnaire: GetUserQuestionsResponse = $state(
	[] as GetUserQuestionsResponse,
);
let answers: { [k: string]: UserAnswerPublic } = $state({});
let showAlert: boolean = $state(false);
let disableEdit: boolean = $state(false);
let alertMessage: string = $state(i18n.tr.userData.alertMessageMissing);
let promise = $state(setup());
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={i18n.tr.userData.alertMessageTitle}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- The actual content -->
	{#await promise}
		<p>{i18n.tr.userData.loadingMessage}</p>
	{:then { questionnaire, answers }}
		<div class="container m-1 mx-auto w-full max-w-xl">
			<Card class="container m-1 mx-auto w-full max-w-xl">
				<Heading
					tag="h3"
					class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
					>{i18n.tr.userData.heading}</Heading
				>
				<form
					class="m-1 mx-auto w-full flex-col space-y-6"
					onsubmit={preventDefault(submitData)}
				>
					{#each questionnaire as element, i}
						{#if element.text && element.component}
						<DataInput
							component={componentTable[element.component]}
							bind:value={answers[element.id].answer}
							bind:additionalValue={answers[element.id]
								.additional_answer}
							label={element?.text[i18n.locale].question}
							textTrigger={element.additional_option}
							required={true}
							additionalRequired={true}
							id={"input_" + String(i)}
							items={element.text[i18n.locale].options_json === "" ? null : JSON.parse(element.text[i18n.locale].options_json)}
							disabled={disableEdit}
						/>
						{/if}
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
								{i18n.tr.userData.changeData}
							</div>
						</Button>
					{:else}
						<Button
							class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
							type="submit">{i18n.tr.userData.submitButtonLabel}</Button
						>
					{/if}
				</form>
			</Card>
		</div>
	{:catch error}
		<AlertMessage
			title={i18n.tr.userData.alertMessageTitle}
			message={error.message}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/await}
