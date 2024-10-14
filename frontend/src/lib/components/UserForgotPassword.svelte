<script lang="ts">
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import { resetForgotPassword } from '$lib/client/services.gen';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { Button, Card, Heading, Input } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';

	const maildata = {
		component: Input,
		type: 'text',
		value: null,
		props: {
			placeholder: $_('user.forgotPw.placeholder')
		}
	};

	let alertMessage: string = $_('user.forgotPw.formatError');
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

	async function submitData(mailstring: string): Promise<void> {
		const data = {
			body: {
				email: mailstring
			},
			throwOnError: true
		};

		await resetForgotPassword(data)
			.then((returned) => {
				console.log('successful transmission, response status: ', returned.response.status);
				showSuccess = true;
			})
			.catch((error) => {
				console.log(error);
				showAlert = true;
				alertMessage = $_('user.forgotPw.sendError');
			});
	}
</script>

{#if showAlert}
	<AlertMessage
		title={$_('user.forgotPw.alertTitle')}
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
		>{$_('user.forgotPw.heading')}</Heading
	>
	{#if showSuccess === false}
		<div class="m-2 mx-auto w-full flex-col space-y-6 p-2">
			<DataInput
				component={maildata.component}
				bind:value={maildata.value}
				properties={maildata.props}
			/>
		</div>

		<div class="m-2 flex w-full items-center justify-center p-2">
			<Button
				size="md"
				on:click={(event) => {
					valid = validateEmail(maildata.value);
					showAlert = !valid;
					if (valid) {
						submitData(maildata.value);
					}
				}}>{$_('user.forgotPw.pending')}</Button
			>
		</div>
	{:else}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<p>{$_('user.forgotPw.mailSentMessage')}</p>
		</div>
		<div class="m-2 flex w-full items-center justify-center p-2">
			<Button
				size="md"
				on:click={(event) => {
					goto(`/${base}`);
				}}>{$_('user.forgotPw.success')}</Button
			>
		</div>
	{/if}
</Card>
