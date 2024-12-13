<svelte:options runes={true}/>
<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Button, Heading, Popover } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";
let { triggeredBy = "" } = $props();
let showAlert: boolean = $state(false);
let alertMessage: string = $state(i18n.tr.login.alertMessageError);
</script>

<Popover {triggeredBy} class="text-gray-700 dark:text-gray-400">
	{#if showAlert}
		<AlertMessage
			title={i18n.tr.login.alertMessageTitle}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}
	{#if user.data !== null}
		<div
			class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6"
		>
			<p class="m-2 w-full rounded-lg p-2 font-semibold">
				{user.data?.email}
			</p>
			<Button
				class="m-2 w-full"
				size="lg"
				type="button"
				href="{base}/userLand/userLandingpage"
				>{i18n.tr.login.profileAccess}</Button
			>
			<Button class="m-2 w-full" on:click={async () => {
				const response = await user.logout();
				if (response.error) {
					alertMessage = i18n.tr.login.alertMessageError;
					showAlert = true;
				} else {
					console.log("Logout successful");
					user.data = null;
					currentChild.id = null;
					currentChild.data = null;
					goto(`/${base}`);
				}

			}} size="lg" type="button"
				>{i18n.tr.login.profileButtonLabelLogout}</Button
			>
		</div>
	{:else}
		<div
			class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6"
		>
			<Heading tag="h3" class="mx-auto flex w-full justify-center"
				>{i18n.tr.login.profileTitleDefault}</Heading
			>
			<Button
				type="button"
				class="m-2 w-full"
				href="{base}/userLand/userLogin"
				size="lg">{i18n.tr.login.profileButtonLabelDefault}</Button
			>
		</div>
	{/if}
</Popover>
