<svelte:options runes={true} />

<script lang="ts">
import {
	authCookieLogin,
	usersCurrentUser,
	usersPatchCurrentUser,
} from "$lib/client/services.gen";
import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Button, Heading, Input, Modal } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";

let newPassword = $state(null) as string | null;
let newPasswordRepeat = $state(null) as string | null;
let currentPassword = $state(null) as string | null;
let currentPasswordValid = $state(false);
let passwordChangeSuccess = $state(false);
let showAlert = $state(false);
let alertMessage = $state(i18n.tr.settings.defaultAlertMessage);

async function submitNewPassword() {
	currentPasswordValid = false;
	passwordChangeSuccess = false;
	showAlert = false;

	if (currentPassword === null || currentPassword === "") {
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordEmptyError;
		return;
	}

	if (newPassword === null || newPassword === "") {
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordEmptyError;
		return;
	}

	if (newPassword !== newPasswordRepeat) {
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordsDontMatchError;
		return;
	}

	if (newPassword === currentPassword) {
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordsTheSameError;
		return;
	}

	const currentUser = await usersCurrentUser();

	if (currentUser.error || !currentUser.data) {
		alertMessage = i18n.tr.settings.getUserError;
		showAlert = true;
		return;
	}

	const verifyResponse = await authCookieLogin({
		body: {
			username: currentUser.data.email,
			password: currentPassword,
		},
	});

	if (verifyResponse.error) {
		alertMessage = i18n.tr.settings.oldPasswordWrong;
		showAlert = true;
		return;
	}

	currentPasswordValid = true;

	const patchResponse = await usersPatchCurrentUser({
		body: {
			password: newPassword,
		},
	});

	if (patchResponse.error) {
		alertMessage = i18n.tr.settings.sendError;
		showAlert = true;
		passwordChangeSuccess = false;
	} else {
		passwordChangeSuccess = true;
	}
}
</script>

{#if showAlert}
	<AlertMessage
		id="alertMessageSettings"
		title={i18n.tr.settings.alertTitle}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<div class="m-2 p-2 flex flex-col space-y-2 text-gray-700 dark:text-gray-400">
	<Heading tag="h4" class="font-bold text-gray-700 dark:text-gray-400" id="changePasswordHeading"
		>{i18n.tr.settings.changePassword}</Heading
	>
	<form
		class="space-y-4 mb-2 pb-2"
		onsubmit={preventDefault(submitNewPassword)}
	>
		<Input
			bind:value={currentPassword}
			type="password"
			id="oldPassword"
			placeholder={i18n.tr.settings.enterPassword}
		/>

		<Input
			bind:value={newPassword}
			type="password"
			id="newPassword"
			placeholder={i18n.tr.settings.newPassword}
		/>

		<Input
			bind:value={newPasswordRepeat}
			type="password"
			id="newPasswordConfirm"
			placeholder={i18n.tr.settings.newPasswordConfirm}
		/>

		<Button id="changePasswordSubmitButton" size="lg" type="submit"
			>{i18n.tr.settings.confirmChange}</Button
		>
	</form>

	<Modal
		id="passwordChangeSuccessModal"
		classBody="flex flex-col pb-2 mb-2 items-center"
		bind:open={passwordChangeSuccess}
		dismissable={false}
	>
		<span class="mb-2 pb-2"
			>{i18n.tr.settings.confirmPasswordChangeSuccess}</span
		>
		<Button
			id="ModalCloseButton"
			type="button"
			on:click={() => {
				newPassword = null;
				newPasswordRepeat = null;
				currentPassword = "";
				currentPasswordValid = false;
				passwordChangeSuccess = false;
			}}>{i18n.tr.settings.closeWindow}</Button
		>
	</Modal>
</div>
