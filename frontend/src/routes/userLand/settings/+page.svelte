<svelte:options runes={true} />

<script lang="ts">
import { goto } from "$app/navigation";
import {
	authCookieLogin,
	deleteCurrentUserAccount,
	usersCurrentUser,
	usersPatchCurrentUser,
} from "$lib/client/sdk.gen";
import DeleteAccountModal from "$lib/components/DeleteAccountModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { isValidPassword, minPasswordLength, preventDefault } from "$lib/util";
import { Button, Heading, Helper, Input, Label, Modal } from "flowbite-svelte";

let newPassword = $state(null) as string | null;
let newPasswordRepeat = $state(null) as string | null;
let currentPassword = $state(null) as string | null;
let currentPasswordValid = $state(false);
let passwordChangeSuccess = $state(false);
let showDeleteAccountModal = $state(false);

async function deleteAccount(dryRun: boolean, password: string) {
	return await deleteCurrentUserAccount({
		body: { password: password },
		query: { dry_run: dryRun },
	});
}

async function afterAccountDeleted() {
	user.data = null;
	await goto("/");
}

async function submitNewPassword() {
	currentPasswordValid = false;
	passwordChangeSuccess = false;

	if (currentPassword === null || currentPassword === "") {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.emptyPasswordError,
			true,
			false,
		);
		return;
	}

	if (newPassword === null || newPassword === "") {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.emptyPasswordError,
			true,
			false,
		);
		return;
	}

	if (!isValidPassword(newPassword)) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.passwordTooShortError.replace(
				"{minLength}",
				String(minPasswordLength),
			),
			true,
			false,
		);
		return;
	}

	if (newPassword !== newPasswordRepeat) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.nonMatchingPasswordsError,
			true,
			false,
		);
		return;
	}

	if (newPassword === currentPassword) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.samePasswordsError,
			true,
			false,
		);
		return;
	}

	const currentUser = await usersCurrentUser();

	if (currentUser.error || !currentUser.data) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.getUserError,
			true,
			false,
		);
		return;
	}

	const verifyResponse = await authCookieLogin({
		body: {
			username: currentUser.data.email,
			password: currentPassword,
		},
	});

	if (verifyResponse.error) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.oldPasswordWrong,
			true,
			false,
		);
		return;
	}

	currentPasswordValid = true;

	const patchResponse = await usersPatchCurrentUser({
		body: {
			password: newPassword,
		},
	});

	if (patchResponse.error) {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.sendError,
			true,
			false,
		);
		passwordChangeSuccess = false;
	} else {
		passwordChangeSuccess = true;
	}
}
</script>


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
                autocomplete="new-password"
                required
                minlength={minPasswordLength}
                placeholder={i18n.tr.settings.placeholder}
        />
        <Helper id="newPasswordRequirement" class="text-sm">
            {i18n.tr.settings.passwordRequirement.replace("{minLength}", String(minPasswordLength))}
        </Helper>

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
                autocomplete="new-password"
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

    <hr class="my-8 border-gray-200 dark:border-gray-700"/>

    <Heading
            tag="h4"
            class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
            id="deleteAccountHeading">{i18n.tr.settings.deleteAccount}</Heading
    >
    <p class="m-2 text-center">{i18n.tr.settings.deleteAccountDescription}</p>
    <div class="m-2 flex justify-center">
        <Button
                id="deleteAccountButton"
                color="red"
                size="lg"
                on:click={() => {showDeleteAccountModal = true;}}
        >{i18n.tr.settings.deleteAccount}</Button
        >
    </div>
</div>

<DeleteAccountModal
        bind:open={showDeleteAccountModal}
        deleteRequest={deleteAccount}
        afterDelete={afterAccountDeleted}
/>
