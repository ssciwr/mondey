<svelte:options runes={true} />

<script lang="ts">
import {
	authCookieLogin,
	usersCurrentUser,
	usersPatchCurrentUser,
} from "$lib/client/services.gen";
import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Button, Heading, Input, Label, Modal } from "flowbite-svelte";
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
		alertMessage = i18n.tr.settings.emptyPasswordError;
		return;
	}

	if (newPassword === null || newPassword === "") {
		showAlert = true;
		alertMessage = i18n.tr.settings.emptyPasswordError;
		return;
	}

	if (newPassword !== newPasswordRepeat) {
		showAlert = true;
		alertMessage = i18n.tr.settings.nonMatchingPasswordsError;
		return;
	}

	if (newPassword === currentPassword) {
		showAlert = true;
		alertMessage = i18n.tr.settings.samePasswordsError;
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
	<Heading
		tag="h4"
		class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		id="changePasswordHeading">{i18n.tr.settings.changePassword}</Heading
	>
	<form
		class="m-2 mx-auto w-full flex-col space-y-6"
		onsubmit={preventDefault(submitNewPassword)}
	>
		<Label
			class="font-semibold text-gray-700 dark:text-gray-400"
			id="oldPasswordLabel"
			for="oldPassword">{i18n.tr.settings.enterPassword}</Label
		>
		<Input
			bind:value={currentPassword}
			type="password"
			id="oldPassword"
			required
			placeholder={i18n.tr.settings.placeholder}
			autocomplete="current-password"
		/>

		<Label
			class="font-semibold text-gray-700 dark:text-gray-400"
			id="newPasswordLabel"
			for="newPassword">{i18n.tr.settings.newPassword}</Label
		>
		<Input
			bind:value={newPassword}
			type="password"
			id="newPassword"
			required
			placeholder={i18n.tr.settings.placeholder}
		/>

		<Label
			class="font-semibold text-gray-700 dark:text-gray-400"
			id="newPasswordConfirmLabel"
			for="newPasswordConfirm"
			>{i18n.tr.settings.newPasswordConfirm}</Label
		>
		<Input
			bind:value={newPasswordRepeat}
			type="password"
			id="newPasswordConfirm"
			required
			placeholder={i18n.tr.settings.placeholder}
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
