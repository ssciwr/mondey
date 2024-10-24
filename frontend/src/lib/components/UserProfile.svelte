<script lang="ts">
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import { authCookieLogout } from '$lib/client/services.gen';
	import { type UserRead } from '$lib/client/types.gen';
	import { currentUser, refresh } from '$lib/stores/userStore';
	import { Button, Heading, Popover } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { get } from 'svelte/store';
	import AlertMessage from './AlertMessage.svelte';

	export let triggeredBy = '';

	let userData: UserRead | null = get(currentUser);
	let showAlert: boolean = false;
	let alertMessage: string = $_('login.alertMessageError');

	onMount(async () => {
		await refresh();
	});

	async function logout(): Promise<void> {
		const response = await authCookieLogout();
		if (response.error) {
			console.log('Error during logout: ', response.response.status, response.error.detail);
			showAlert = true;
			alertMessage += ': ' + response.error.detail;
		} else {
			console.log('Successful logout of user ', userData?.email, response.response.status);
			userData = null;
			goto(`/${base}`);
		}
	}
</script>

<Popover {triggeredBy} class="text-gray-700 dark:text-gray-400">
	{#if showAlert}
		<AlertMessage
			title={$_('login.alertMessageTitle')}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}
	{#if userData !== null}
		<div class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6">
			<p class="m-2 w-full rounded-lg p-2 font-semibold">{userData.email}</p>
			<Button class="m-2 w-full" on:click={logout} size="lg"
				>{$_('login.profileButtonLabelLogout')}</Button
			>
		</div>
	{:else}
		<div class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6">
			<Heading tag="h3" class="mx-auto flex w-full justify-center"
				>{$_('login.profileTitleDefault')}</Heading
			>
			<Button class="m-2 w-full" href="{base}/userLand/userLogin" size="lg"
				>{$_('login.profileButtonLabelDefault')}</Button
			>
		</div>
	{/if}
</Popover>
