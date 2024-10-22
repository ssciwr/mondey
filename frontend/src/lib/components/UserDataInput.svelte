<script lang="ts">
	import {
		createUserAnswers,
		getCurrentUserAnswers,
		getUserQuestions,
		updateCurrentUserAnswers,
		usersCurrentUser
	} from '$lib/client/services.gen';
	import { type GetUserQuestionsResponse, type UserAnswerPublic } from '$lib/client/types.gen';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	function convertQuestions(questionnaire: GetUserQuestionsResponse): GetUserQuestionsResponse {
		// TODO: once questions come from the database we can do this with the questionnaire
		// different algorithm that makes use of the component lookup table in '$lib/stores' is needed here then.
		questionnaire.map((e) => {
			return e;
		});
		return questionnaire;
	}

	function convertAnswers(questionnaire: GetUserQuestionsResponse | undefined): UserAnswerPublic[] {
		// TODO: once questions come from the database we can do this with the questionnaire
		// his version is temporary until the underlying datastructure has been changed to accomodate
		// the backend models

		return data.map((e, index) => {
			if (e.additionalValue !== '' && e.additionalValue !== null) {
				return {
					id: index,
					answer: String(e.additionalValue)
				} as UserAnswerPublic;
			} else {
				return {
					id: index,
					answer: String(e.value)
				} as UserAnswerPublic;
			}
		});
	}

	async function submitData() {
		const answers = convertAnswers(questionnaire);
		console.log('answers: ', answers);

		const response = await updateCurrentUserAnswers({
			body: answers,
			query: { session_id: userID }
		});

		if (response.error) {
			console.log('Error happened when sending user question answers: ', response.error);
			alertMessage = $_('userData.alertMessageError');
			showAlert = true;
		} else {
			console.log('successfully sent data to backend, yay!');

			// disable all elements to make editing a conscious choice
			for (let element of data) {
				element.disabled = true;
			}
			dataIsCurrent = true;
		}
	}

	// README: is storing userID a problem?
	let userID: number | undefined;

	// this can, but does not have to, come from a database later.
	export let data: any[];

	// this is the data that will be used in the end
	let questionnaire: GetUserQuestionsResponse | undefined = [];

	// flags for enabling and disabling visual hints
	let showAlert: boolean = false;
	let dataIsCurrent: boolean = false;
	$: reload = false;

	// what is shown in the alert if showAlert === true
	let alertMessage: string = $_('userData.alertMessageMissing');

	// load questions and current answers from server and put them into the data
	// structure that the UserDataInput component understands
	onMount(async () => {
		console.log('onmount');
		const currentUser = await usersCurrentUser();

		if (currentUser.error) {
			showAlert = true;
			alertMessage = 'current user could not be found. log out and try again';
		} else {
			userID = currentUser?.data?.id;

			const userQuestions = await getUserQuestions();

			if (userQuestions.error) {
				showAlert = true;
				alertMessage = $_('userData.alertMessageError');
				console.log('questions could not be retrieved.', userQuestions?.error);
			} else {
				questionnaire = convertQuestions(userQuestions?.data as GetUserQuestionsResponse);
				console.log('data from backend: ', 'questionnaire: ', questionnaire);
			}

			// get current answers. if nothing is there, create a set of empty answers
			let currentAnswers = await getCurrentUserAnswers();

			if (currentAnswers?.error) {
				showAlert = true;
				console.log('answers could not be retrieved.', currentAnswers?.error);
				alertMessage = $_('userData.alertMessageError');
			} else if (currentAnswers?.data?.length === 0) {
				const createAnswerResponse = await createUserAnswers({
					// TODO: replace this with questionnaire based algo
					// once that is fixed
					body: data.map((e, index) => {
						return {
							id: index,
							answer: ''
						};
					})
				});

				if (createAnswerResponse.error) {
					console.log('Something went wrong when adding default answers');
					showAlert = true;
					alertMessage = $_('userData.alertMessageError');
				} else {
					console.log('Creation of empty answers successful');
				}
			} else {
				console.log('data from backend: ', 'currentAnswers: ', currentAnswers?.data);
				for (let i = 0; i < data.length; i++) {
					data[i].value = currentAnswers.data[i].answer;
					data[i].disabled = true;
					dataIsCurrent = true;
				}
			}
		}
		console.log('onmount done');
		reload = true;
	});
	console.log(
		'data: ',
		data.map((e) => {
			e.value;
		})
	);
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
			{#each data as element, i}
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
					class="dark:bg-primay-700 bg-primary-700 hover:bg-primary-800 dark:hover:bg-primary-800 w-full text-center text-sm text-white hover:text-white"
					on:click={() => {
						console.log('dataiscurrent click');
						for (let element of data) {
							element.disabled = false;
						}
						dataIsCurrent = false;
					}}
				>
					<div class="flex items-center justify-center">{$_('userData.changeData')}</div>
				</Button>
			{:else}
				<Button
					class="dark:bg-primay-700 bg-primary-700 hover:bg-primary-800 dark:hover:bg-primary-800 w-full text-center text-sm text-white hover:text-white"
					type="submit">{$_('userData.submitButtonLabel')}</Button
				>
			{/if}
		</form>
	</Card>
</div>
