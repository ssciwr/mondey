<svelte:options runes={true} />
<script lang="ts">
import { resetResetPassword, usersPatchCurrentUser } from "$lib/client";

import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Button, Heading, Input, Label, Modal } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";

let new_email = $state(null) as string | null;
let new_email_repeat = $state(null) as string | null;
let new_password = $state(null) as string | null;
let new_password_repeat = $state(null) as string | null;
let current_password = $state(null) as string | null;
let showSuccessMail = $state(false);
let showSuccessPassword = $state(false);
let showAlert = $state(false);
let alertMessage = $state(i18n.tr.forgotPw.formatError);

function submitNewEmail() {
	if (new_email === null || new_email === "") {
		console.log("email is empty");
		showAlert = true;
		return;
	}

	if (new_email !== new_email_repeat) {
		console.log("emails do not match");
		showAlert = true;
		return;
	}

	console.log(`email changed ${new_email} ${new_email_repeat}`);

	// FIXME: tthis is the wrong endpoint. Needs verification first
	// see: https://owasp.org/www-community/pages/controls/Changing_Registered_Email_Address_For_An_Account
	const response = {};
	if (response.error) {
		console.log("error: ", response.error);
		alertMessage = i18n.tr.forgotPw.sendError;
		showAlert = true;
	} else {
		showSuccessMail = true;
	}
}

function submitNewPassword() {
	if (new_password === null || new_password === "") {
		console.log("password is empty");
		showAlert = true;
		return;
	}

	if (new_password !== new_password_repeat) {
		console.log("passwords do not match");
		showAlert = true;
		return;
	}

	console.log(
		`password change clicked ${current_password} ${new_password} ${new_password_repeat}`,
	);

	const response = {};
	if (response.error) {
		console.log("error: ", response.error);
		alertMessage = i18n.tr.forgotPw.sendError;
		showAlert = true;
	} else {
		showSuccessPassword = true;
	}
}
</script>



{#if showAlert}
	<AlertMessage
		title={i18n.tr.forgotPw.alertTitle}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<div class="m-2 p-2 flex flex-col space-y-2 text-gray-700 dark:text-gray-400 ">
    <Heading tag="h2" class="font-bold text-gray-700 dark:text-gray-400">{i18n.tr.userData.settings}</Heading>

	<Heading tag="h4" class="font-bold text-gray-700 dark:text-gray-400">{i18n.tr.userData.changeEmail}</Heading>
    <form class = "space-y-4 mb-2 pb-2" onsubmit={preventDefault(submitNewEmail)}>
        <Input id="change-email" type="email" placeholder={i18n.tr.userData.newEmail} bind:value={new_email}/>
        <Input id="change-email-confirm" type="email" placeholder={i18n.tr.userData.newEmailConfirm} bind:value={new_email_repeat}/>
        <Button size="lg" type="submit">{i18n.tr.userData.changeEmail}</Button>
	</form>

	<div class = "flex flex-row pb-2 mb-2 items-center">
		<Modal class = "m-2 p-2" title={i18n.tr.userData.confirmChange} bind:open={showSuccessMail} dismissable={true}>
			{i18n.tr.userData.confirmChangeSuccess}
		</Modal>
	</div>

	<Heading tag="h4" class="font-bold text-gray-700 dark:text-gray-400">{i18n.tr.userData.changePassword}</Heading>
    <form class = "space-y-4 mb-2 pb-2" onsubmit={preventDefault(submitNewPassword)}>
        <Input
            bind:value={current_password}
            type="password"
            id="old_password"
            placeholder={i18n.tr.userData.oldPassword}
        />

        <Input
            bind:value={new_password}
            type="password"
            id="new_password"
            placeholder={i18n.tr.userData.newPassword}
        />

        <Input
            bind:value={new_password_repeat}
            type="password"
            id="new_password-confirm"
            placeholder={i18n.tr.userData.newPasswordConfirm}
        />
        <Button size="lg" type="submit">{i18n.tr.userData.changePassword}</Button>
    </form>

	<div class = "flex flex-row pb-2 mb-2 items-center">
		<Modal class = "m-2 p-2" title={i18n.tr.userData.confirmChange} bind:open={showSuccessPassword} dismissable={true}>
			{i18n.tr.userData.confirmChangeSuccess}
		</Modal>
	</div>
</div>
