<svelte:options runes={true} />
<script lang="ts">
import {
	authCookieLogin,
	usersCurrentUser,
	usersPatchCurrentUser,
} from "$lib/client/services.gen";
import { type AuthCookieLoginData } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Button, Heading, Input, Modal } from "flowbite-svelte";
import AlertMessage from "./AlertMessage.svelte";

let new_password = $state(null) as string | null;
let new_password_repeat = $state(null) as string | null;
let currentPassword = $state(null) as string | null;
let currentPasswordValid = $state(false);
let showSuccessPassword = $state(false);
let showAlert = $state(false);
let alertMessage = $state(i18n.tr.forgotPw.formatError);

async function submitCurrentPassword(): Promise<boolean> {
	if (currentPassword === null || currentPassword === "") {
		console.log("password is empty");
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordEmpty;
		return false;
	}

	console.log(`password submit clicked ${currentPassword}`);
	const currentUser = await usersCurrentUser();

	if (currentUser.error || !currentUser.data) {
		console.log("error: ", currentUser.error);
		alertMessage = i18n.tr.settings.oldPasswordWrong;
		showAlert = true;
		return false;
	}

	const response = await authCookieLogin({
		body: {
			username: currentUser.data.email,
			password: currentPassword,
		},
	});

	if (response.error) {
		console.log("error: ", response.error);
		alertMessage = i18n.tr.settings.oldPasswordWrong;
		showAlert = true;
		return false;
	}

	currentPasswordValid = true;
	currentPassword = "";
	return true;
}

async function submitNewPassword() {
	const currentPasswordStatus = submitCurrentPassword();

	if (!currentPasswordStatus) {
		return;
	}

	if (new_password === null || new_password === "") {
		console.log("password is empty");
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordEmpty;
		return;
	}

	if (new_password !== new_password_repeat) {
		console.log("passwords do not match");
		showAlert = true;
		alertMessage = i18n.tr.settings.passwordsDontMatch;
		return;
	}

	console.log(
		`password change clicked ${currentPassword} ${new_password} ${new_password_repeat}`,
	);

	const response = await usersPatchCurrentUser({
		body: {
			password: new_password,
		},
	});

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
		id="alertMessageSettings"
		title={i18n.tr.forgotPw.alertTitle}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<div class="m-2 p-2 flex flex-col space-y-2 text-gray-700 dark:text-gray-400 ">
	<Heading tag="h4" class="font-bold text-gray-700 dark:text-gray-400">{i18n.tr.settings.changePassword}</Heading>
    <form class = "space-y-4 mb-2 pb-2" onsubmit={preventDefault(submitNewPassword)}>
        <Input
            bind:value={currentPassword}
            type="password"
            id="old_password"
            placeholder={i18n.tr.settings.oldPassword}
        />

        <Input
            bind:value={new_password}
            type="password"
            id="new_password"
            placeholder={i18n.tr.settings.newPassword}
        />

        <Input
            bind:value={new_password_repeat}
            type="password"
            id="new_password-confirm"
            placeholder={i18n.tr.settings.newPasswordConfirm}
        />

        <Button id="changePasswordSubmitButton" size="lg" type="submit">{i18n.tr.settings.changePassword}</Button>
    </form>

	<div class = "flex flex-row pb-2 mb-2 items-center">
		<Modal id="passwordChangeSuccessModal" class = "m-2 p-2" title={i18n.tr.settings.confirmChange} bind:open={showSuccessPassword} dismissable={true}>
			{i18n.tr.settings.confirmChangeSuccess}
		</Modal>
	</div>
</div>
