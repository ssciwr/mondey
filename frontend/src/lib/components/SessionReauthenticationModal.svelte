<svelte:options runes={true} />

<script lang="ts">
import { reauthenticateSession } from "$lib/client/sdk.gen";
import { i18n } from "$lib/i18n.svelte";
import { sessionStore } from "$lib/stores/sessionStore.svelte";
import { Button, Input, Label, Modal } from "flowbite-svelte";

let password = $state("");
let errorMessage = $state("");
let submitting = $state(false);

async function reauthenticate() {
	errorMessage = "";
	submitting = true;
	try {
		const result = await reauthenticateSession({ body: { password } });

		if (result.error) {
			if (result.response?.status === 400) {
				errorMessage = i18n.tr.login.incorrectPassword;
			} else if (result.response?.status !== 401) {
				errorMessage = i18n.tr.login.reauthenticationError;
			}
			return;
		}

		// The response interceptor also processes these headers. Updating here keeps
		// this component correct if it is used without the root interceptor.
		if (result.response) {
			sessionStore.updateFromResponse(result.response);
		}
		sessionStore.isReauthenticationShown = false;
	} catch {
		if (sessionStore.isReauthenticationShown) {
			errorMessage = i18n.tr.login.reauthenticationError;
		}
	} finally {
		password = "";
		submitting = false;
	}
}

function submit(event: SubmitEvent) {
	event.preventDefault();
	void reauthenticate();
}
</script>

<Modal
	bind:open={sessionStore.isReauthenticationShown}
	title={i18n.tr.login.sessionExpiringTitle}
	dismissable={false}
	size="sm"
>
	<form class="space-y-4" onsubmit={submit}>
		<p class="text-gray-700 dark:text-gray-300">
			{i18n.tr.login.sessionAbsoluteExpiringMessage}
		</p>
		<div>
			<Label for="session-reauthentication-password" class="mb-2">
				{i18n.tr.login.passwordLabel}
			</Label>
			<Input
				id="session-reauthentication-password"
				type="password"
				autocomplete="current-password"
				bind:value={password}
				disabled={submitting}
				required
				autofocus
			/>
		</div>
		{#if errorMessage}
			<p class="text-sm text-red-700 dark:text-red-400" role="alert">
				{errorMessage}
			</p>
		{/if}
		<Button type="submit" disabled={submitting}>
			{i18n.tr.login.reauthenticate}
		</Button>
	</form>
</Modal>
