<script lang="ts">
	import { base } from '$app/paths';
	import { registerRegister } from '$lib/client/services.gen';
	import { type RegisterRegisterData } from '$lib/client/types.gen';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import UserVerify from '$lib/components/UserVerify.svelte';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading, Input, Label, Select } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';

	// FIXME: try and simplify this further
	async function submitData(): Promise<void> {
		const equalPW = password !== '' && password === passwordconfirm;

		const userData: RegisterRegisterData = {
			body: {
				email: email,
				password: password,
				is_active: true,
				is_superuser: false,
				is_researcher: false
			}
		};
		if (equalPW) {
			userData.body.is_researcher = role === $_('registration.researcherRole');
			userData.body.is_superuser = role === $_('registration.adminRole');

			const result = await registerRegister(userData);

			if (result.error) {
				console.log('error: ', result.response.status, result.error.detail);
				alertMessage = $_('registration.alertMessageError') + ': ' + result.error.detail;
				showAlert = true;
			} else {
				console.log('successful transmission: ', result.response.status);
				success = true;
			}
		} else {
			showAlert = true;
			alertMessage = $_('registration.alertMessagePasswords');
		}
	}

	let email: string = '';
	let password: string = '';
	let passwordconfirm: string = '';
	let role: string = $_('registration.observerRole');
	let showAlert: boolean = false;
	let success: boolean = false;
	let alertMessage = $_('registration.alertMessageMissing');
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('registration.alertMessageTitle')}
		message={alertMessage}
		infopage="{base}/info"
		infotitle="Was passiert mit den Daten"
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- The actual content -->
<Card class="container m-2 mx-auto w-full max-w-xl p-2">
	<Heading
		tag="h3"
		class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{$_('registration.heading')}
	</Heading>

	{#if success === false}
		<form onsubmit={preventDefault(submitData)} class="m-2 mx-auto w-full flex-col space-y-6">
			<Label for={'username'} class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_('registration.emailLabel')}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={email}
					required
					type="email"
					id="email"
					placeholder={$_('registration.emailLabel')}
				/>
			</div>

			<Label for={'password'} class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_('registration.passwordLabel')}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={password}
					required
					type="password"
					id="password"
					placeholder={$_('registration.passwordLabel')}
				/>
			</div>

			<Label for={'password_confirm'} class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_('registration.passwordConfirmLabel')}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={passwordconfirm}
					required
					type="password"
					id="password"
					placeholder={$_('registration.passwordConfirmLabel')}
				/>
			</div>

			<Label for={'role'} class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_('registration.role')}</Label
			>
			<div class="space-y-4">
				<Select
					bind:value={role}
					items={[
						$_('registration.observerRole'),
						$_('registration.researcherRole'),
						$_('registration.adminRole')
					].map((v) => {
						return { name: String(v), value: v };
					})}
					id="role"
					required
					placeholder={$_('registration.selectPlaceholder')}
				/>
			</div>

			<Button
				type="submit"
				class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				>{$_('registration.submitButtonLabel')}</Button
			>
		</form>
	{:else}
		<UserVerify />
	{/if}
</Card>
