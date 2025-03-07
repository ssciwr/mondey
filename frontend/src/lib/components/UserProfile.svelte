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
		</div>
	{/if}
</Popover>
