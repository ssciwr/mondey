<script lang="ts">
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { Button, Card, Heading, Input } from 'flowbite-svelte';

	const heading = 'Passwort vergessen?';
	const maildata = {
		component: Input,
		type: 'text',
		value: null,
		props: {
			placeholder: 'Bitte geben sie eine E-mail Adresse an um ihr Passwort zu erneuern'
		}
	};
	const successButtonLabel: string = 'Zurück zur Startseite';
	const pendingButtonLabel: string = 'Absenden';
	const mailSentMessage: string = 'Überprüfen sie ihr E-Mail Postfach';
	const alertTitle: string = 'Fehler';

	let alertMessage: string = 'Die angegebene email Adresse hat ein falsches Format';
	let valid: boolean = true;
	let showAlert: boolean = !valid;
	let showSuccess: boolean = false;

	function validateEmail(value: string | null): boolean {
		if (value === null) {
			return false;
		} else {
			const mailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			return mailRegex.test(value);
		}
	}

	function fetchDummy(endpoint: string, data: any): any {
		return {
			ok: true
		};
	} // README: this is a dummy. Needs to be replaced with real backend call later

	// FIXME: check how this is done with the current API. needs to be integrated.
	async function submitData(mailstring: string | null): Promise<void> {
		try {
			const response = await fetchDummy('api/forgot-password', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(mailstring)
			});

			if (!response.ok) {
				throw new Error('Network error');
			} else {
				showSuccess = true;
			}
		} catch (error) {
			console.log(error);
			showAlert = true;
			alertMessage = 'Beim Senden ist ein Fehler aufgetreten';
		}
	}
</script>

{#if showAlert}
	<AlertMessage
		title={alertTitle}
		message={alertMessage}
		lastpage={`${base}/userLand/lostPassword`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<Card class="container m-2 mx-auto w-full max-w-xl items-center justify-center p-2">
	<Heading
		tag="h3"
		class="m-2 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{heading}</Heading
	>
	{#if showSuccess === false}
		<div class="m-2 mx-auto w-full flex-col space-y-6 p-2">
			<DataInput
				component={maildata.component}
				bind:value={maildata.value}
				properties={maildata.props}
			/>
		</div>
	{:else}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<p>{mailSentMessage}</p>
		</div>
	{/if}

	{#if showSuccess === false}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<Button
				size="md"
				on:click={(event) => {
					valid = validateEmail(maildata.value);
					showAlert = !valid;
					if (valid) {
						submitData(maildata.value);
					}
				}}>{pendingButtonLabel}</Button
			>
		</div>
	{:else}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<Button
				size="md"
				on:click={(event) => {
					goto(`/${base}`);
				}}>{successButtonLabel}</Button
			>
		</div>
	{/if}
</Card>
