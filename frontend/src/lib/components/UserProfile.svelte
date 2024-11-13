<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import { authCookieLogout } from "$lib/client/services.gen";
import { currentChild } from "$lib/stores/childrenStore";
import { currentUser, refreshUser } from "$lib/stores/userStore";
import { Button, Heading, Popover } from "flowbite-svelte";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let { triggeredBy = "" } = $props();
let showAlert: boolean = $state(false);
let alertMessage: string = $state($_("login.alertMessageError"));

onMount(async () => {
	await refreshUser();
});

async function logout(): Promise<void> {
	const response = await authCookieLogout();
	if (response.error) {
		console.log(
			"Error during logout: ",
			response.response.status,
			response.error.detail,
		);
		showAlert = true;
		alertMessage += ": " + response.error.detail;
	} else {
		console.log(
			"Successful logout of user ",
			$currentUser?.email,
			response.response.status,
		);
		currentUser.set(null);
		currentChild.set(null);
		goto(`/${base}`);
	}
}
</script>

<Popover {triggeredBy} class="text-gray-700 dark:text-gray-400">
	{#if showAlert}
		<AlertMessage
			title={$_("login.alertMessageTitle")}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}
	{#if $currentUser !== null}
		<div
			class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6"
		>
			<p class="m-2 w-full rounded-lg p-2 font-semibold">
				{$currentUser?.email}
			</p>
			<Button
				class="m-2 w-full"
				size="lg"
				type="button"
				href="{base}/userLand/userLandingpage"
				>{$_("login.profileAccess")}</Button
			>
			<Button class="m-2 w-full" on:click={logout} size="lg" type="button"
				>{$_("login.profileButtonLabelLogout")}</Button
			>
		</div>
	{:else}
		<div
			class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6"
		>
			<Heading tag="h3" class="mx-auto flex w-full justify-center"
				>{$_("login.profileTitleDefault")}</Heading
			>
			<Button
				type="button"
				class="m-2 w-full"
				href="{base}/userLand/userLogin"
				size="lg">{$_("login.profileButtonLabelDefault")}</Button
			>
		</div>
	{/if}
</Popover>
