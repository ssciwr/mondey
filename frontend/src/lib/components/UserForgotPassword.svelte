<script lang="ts">
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { lang_id } from '$lib/stores/langStore';
	import { Button, Card, Heading, Input } from 'flowbite-svelte';
	import { onDestroy, onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { get } from 'svelte/store';

	const heading = $_('user.forgotPw.heading');
	const maildata = {
		component: Input,
		type: 'text',
		value: null,
		props: {
			placeholder: $_('user.forgotPw.placeholder')
		}
	};
	const successButtonLabel: string = $_('user.forgotPw.success');
	const pendingButtonLabel: string = $_('user.forgotPw.pending');
	const mailSentMessage: string = $_('user.forgotPw.mailSentMessage');
	const alertTitle: string = $_('user.forgotPw.alertTitle');

	let alertMessage: string = $_('user.forgotPw.alertMessage');
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
			alertMessage = $_('user.forgotPw.sendError');
		}
	}

	let unsubscribe: () => void;

	onMount(async () => {
		unsubscribe = await lang_id.subscribe(() => {
			console.log('language changed: ', get(lang_id));
		});
	});

	onDestroy(() => {
		unsubscribe();
	});
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
