<script lang="ts">
	import {
		getCurrentUserAnswers,
		getUserQuestions,
		updateCurrentUserAnswers,
		usersCurrentUser
	} from '$lib/client/services.gen';
	import { type GetUserQuestionsResponse, type UserAnswerPublic } from '$lib/client/types.gen';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { componentTable } from '$lib/stores/componentStore';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading } from 'flowbite-svelte';
	import { onMount, type Component } from 'svelte';
	import { _, locale } from 'svelte-i18n';

	interface QuestionaireProps {
		label: string;
		type: string;
		required: Boolean;
		disabled: Boolean;
		items: any[];
		textTrigger: string | undefined;
	}

	interface QuestionaireElement {
		component: Component;
		value: String | null;
		additionalValue: String | null;
		props: QuestionaireProps;
	}

	function convertQuestions(questionaire: GetUserQuestionsResponse): QuestionaireElement[] {
		return questionaire.map((element) => {
			console.log('question element');
			return {
				component: componentTable[element.component],
				value: null,
				additionalValue: null,
				props: {
					items: JSON.parse(element?.text[$locale].options_json),
					label: element?.text[$locale].question,
					type: 'text',
					required: true,
					disabled: false,
					textTrigger: element.additional_option
				}
			};
		});
	}

	function convertAnswers(questionaire: QuestionaireElement[]): UserAnswerPublic[] {
		return questionaire.map((e, index) => {
			if (
				e.additionalValue !== '' &&
				e.additionalValue !== null &&
				e.value === e.props.textTrigger
			) {
				return {
					question_id: index,
					answer: String(e.value),
					additional_answer: String(e.additionalValue)
				} as UserAnswerPublic;
			} else {
				return {
					question_id: index,
					answer: String(e.value),
					additional_answer: ''
				} as UserAnswerPublic;
			}
		});
	}

	async function submitData() {
		const answers = convertAnswers(questionaire);
		const currentUser = await usersCurrentUser();
		if (currentUser.error) {
			showAlert = true;
			alertMessage = $_('userData.alertMessageUserNotFound');
		}

		const response = await updateCurrentUserAnswers({
			body: answers
		});

		if (response.error) {
			console.log('Error happened when sending user question answers: ', response.error);
			alertMessage = $_('userData.alertMessageError');
			showAlert = true;
		} else {
			console.log('successfully sent data to backend, yay!');
			console.log('answers sent: ', answers);
			console.log(
				'original answers: ',
				questionaire.map((e) => {
					return [e.value, e.additionalValue];
				})
			);

			// disable all elements to make editing a conscious choice
			for (let element of questionaire) {
				element.props.disabled = true;
			}
			questionaire = [...questionaire];
			dataIsCurrent = true;
		}
	}

	// this is the data that will be used in the end
	let questionaire: any[] = [];

	// flags for enabling and disabling visual hints
	let showAlert: boolean = false;
	let dataIsCurrent: boolean = false;

	// what is shown in the alert if showAlert === true
	let alertMessage: string = $_('userData.alertMessageMissing');

	// load questions and current answers from server and put them into the data
	// structure that the UserDataInput component understands
	onMount(async () => {
		console.log('onmount');

		const userQuestions = await getUserQuestions();
		console.log('userquestions from backend', userQuestions);

		if (userQuestions.error) {
			showAlert = true;
			alertMessage = $_('userData.alertMessageError');
			console.log('questions could not be retrieved.', userQuestions?.error);
		} else {
			questionaire = convertQuestions(userQuestions?.data as GetUserQuestionsResponse);
			console.log('data from backend: ', 'questionaire: ', questionaire);
		}

		// get current answers.
		let currentAnswers = await getCurrentUserAnswers();
		console.log('user answers from backend', currentAnswers);

		if (currentAnswers?.error) {
			showAlert = true;
			console.log('answers could not be retrieved.', currentAnswers?.error);
			alertMessage = $_('userData.alertMessageError');
		} else if (currentAnswers?.data.length === 0) {
			console.log('currently no answers'); // debug output. Can go later
		} else {
			for (let i = 0; i < currentAnswers?.data.length; i++) {
				if (
					currentAnswers?.data[i].additional_answer !== null &&
					currentAnswers?.data[i].additional_answer !== undefined &&
					currentAnswers?.data[i].additional_answer !== ''
				) {
					console.log('with additional: ', currentAnswers.data[i]);
					questionaire[i].additionalValue = currentAnswers.data[i].additional_answer;
					console.log(
						'displayed thing: ',
						questionaire[i].props.textTrigger,
						'label: ',
						questionaire[i].props.items.slice(-1)[0]
					);
					questionaire[i].value = questionaire[i].props.items.slice(-1)[0].value;
					console.log('end result: ', questionaire[i]);
				} else {
					console.log('without additional: ', currentAnswers.data[i]);

					questionaire[i].value = currentAnswers.data[i].answer;
				}
				questionaire[i].props.disabled = true;
				dataIsCurrent = true;
				questionaire = [...questionaire]; // TODO: forces a rerender. need a better way to do this
			}
		}
		console.log('onmount done: ', questionaire);
	});
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('userData.alertMessageTitle')}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- The actual content -->
<div class="container m-1 mx-auto w-full max-w-xl">
	<Card class="container m-1 mx-auto w-full max-w-xl">
		<Heading
			tag="h3"
			class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
			>{$_('userData.heading')}</Heading
		>

		<form class="m-1 mx-auto w-full flex-col space-y-6" onsubmit={preventDefault(submitData)}>
			{#each questionaire as element, i}
				<DataInput
					component={element.component}
					bind:value={element.value}
					bind:additionalInput={element.additionalValue}
					label={element.props.label}
					properties={element.props}
					textTrigger={element.props.textTrigger}
					eventHandlers={{
						'on:change': element.onchange,
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
					additionalEventHandlers={{
						'on:change': element.onchange,
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
				/>
			{/each}
			{#if dataIsCurrent === true}
				<Button
					type="button"
					class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
					on:click={() => {
						console.log('dataiscurrent click');
						for (let element of questionaire) {
							element.props.disabled = false;
						}

						// README: this forces a rerender. It is necessary because svelte does not react to nested references being changed. There must be a better solution to this? Svelte 5 runes would be one that comes to mind.
						questionaire = [...questionaire];

						dataIsCurrent = false;
					}}
				>
					<div class="flex items-center justify-center">{$_('userData.changeData')}</div>
				</Button>
			{:else}
				<Button
					class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
					type="submit">{$_('userData.submitButtonLabel')}</Button
				>
			{/if}
		</form>
	</Card>
</div>
