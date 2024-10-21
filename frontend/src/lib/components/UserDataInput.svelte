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

	function convertQuestions(questionaire: GetUserQuestionsResponse) {
		// TODO: once questions come from the database we can do this with the questionaire

		questionaire.map((e) => {
			return e;
		});
	}

	function convertAnswers(questionaire: GetUserQuestionsResponse | undefined): UserAnswerPublic[] {
		// TODO: once questions come from the database we can do this with the questionaire
		// for (let element of questionaire) {
		// }

		return data.map((e, index) => {
			return {
				id: index,
				answer: String(e.value)
			} as UserAnswerPublic;
		});
	}

	function validate(): boolean {
		missingValues = data.map((element) => element.value === '' || element.value === null);
		return missingValues.every((v) => v === false);
	}

	async function submitData() {
		const valid = validate();

		console.log('data: ', data);

		if (valid) {
			const answers = convertAnswers(questionaire);
			console.log('answers: ', answers);

			const response = await updateCurrentUserAnswers({
				body: answers,
				query: { session_id: userID }
			});

			console.log('response on update: ', response);

			if (response.error) {
				console.log('shit happened when sending user question answers: ', response.error);
				showAlert = true;
				alertMessage = 'shit happened when sending user question answers: ' + response.error;
			} else {
				console.log('alright, yay!');
			}
		} else {
			showAlert = true;
		}
	}

	let userID: number | undefined;

	// this can, but does not have to, come from a database later.
	export let data: any[];

	// this is the data that will be used in the end
	let questionaire: GetUserQuestionsResponse | undefined = [];

	onMount(async () => {
		const currentUser = await usersCurrentUser();

		if (currentUser.error) {
			showAlert = true;
			alertMessage = 'current user could not be found. log out and try again';
		} else {
			console.log('current user: ', currentUser?.data?.email, currentUser?.data?.id);
			userID = currentUser?.data?.id;

			const getUserQuestionsResponse = await getUserQuestions();

			if (getUserQuestionsResponse.error) {
				showAlert = true;
				alertMessage =
					'questionaire could not be retrieved. Execute the proper rituals to apeace the machine spirits';
			} else {
				questionaire = getUserQuestionsResponse?.data;
				console.log('data from backend: ', 'questionaire: ', questionaire);
			}

			let currentAnswers;
			try {
				currentAnswers = await getCurrentUserAnswers();
			} catch (error) {
				console.log('Error happened when getting current answers:', error);
			}
			if (currentAnswers?.error) {
				showAlert = true;
				alertMessage =
					'answers could not be retrieved. Execute the proper rituals to apeace the machine spirits';
			} else {
				console.log('data from backend: ', 'currentAnswers: ', currentAnswers?.data);
			}

			if (currentAnswers?.data?.length === 0) {
				const createAnswerResponse = await createUserAnswers({
					body: data.map((e, index) => {
						return {
							id: index,
							answer: ''
						};
					})
				});

				if (createAnswerResponse.error) {
					console.log('shit happened when adding dummy answers');
				} else {
					console.log('creation of empty answers successful');
				}
			}
		}
	});

	let missingValues = data.map(() => false);

	let showAlert: boolean = true;

	let alertMessage: string = 'Bitte füllen Sie die benötigten Felder (hervorgehoben) aus.';

	const buttons = [
		{
			label: 'Abschließen',
			onclick: submitData,
			disabled: true
		}
	];
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
						'on:change': (e) => {
							buttons[0].disabled = false;
							if (element.onchange) {
								element.onchange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
					additionalEventHandlers={{
						'on:change': (e) => {
							buttons[0].disabled = false;
							if (element.additionalOnChange) {
								element.additionalOnChange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
				/>
			{/each}
			<Button
				class="dark:bg-primay-700 bg-primary-700 hover:bg-primary-800 dark:hover:bg-primary-800 w-full text-center text-sm text-white hover:text-white"
				type="submit">{$_('userData.submitButtonLabel')}</Button
			>
		</form>
	</Card>
</div>
