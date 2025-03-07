<svelte:options runes={true} />
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Button, Heading, Input, Label, Modal } from "flowbite-svelte";

let new_email = null as string | null;
let new_email_repeat = null as string | null;
let new_password = null as string | null;
let new_password_repeat = null as string | null;
let showSuccessMail = $state(false);
let showSuccessPassword = $state(false);
let showAlert = $state(false);
let alertMessage = $state(i18n.tr.forgotPw.formatError);

async function submitNewEmail() {
	if (new_email === null || new_email === "") {
		showAlert = true;
		return;
	}

	if (new_email !== new_email_repeat) {
		showAlert = true;
		return;
	}

	console.log(`email changed ${new_email} ${new_email_repeat}`);

	const response = await usersPatchCurrentUser({
		body: {
			email: new_email,
		},
	});

	if (response.error) {
		console.log("error: ", response.error);
		alertMessage = i18n.tr.forgotPw.sendError;
		showAlert = true;
	} else {
		showSuccessMail = true;
	}
}

async function submitNewPassword() {
	if (new_password === null || new_password === "") {
		showAlert = true;
		return;
	}

	if (new_password !== new_password_repeat) {
		showAlert = true;
		return;
	}

	console.log(`password change clicked ${new_password} ${new_password_repeat}`);

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
		title={i18n.tr.forgotPw.alertTitle}
		message={alertMessage}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<div class="m-2 p-2 flex flex-col text-gray-700 dark:text-gray-400 ">
    <Heading tag="h2" class="font-bold text-gray-700 dark:text-gray-400">{i18n.tr.userData.settings}</Heading>

    <form class = "space-y-4 mb-2 pb-2" onsubmit={preventDefault(submitNewEmail)}>
        <Label for="change-email" class="font-semibold text-gray-700 dark:text-gray-400">{i18n.tr.userData.changeEmail}</Label>
        <Input id="change-email" type="email" placeholder={i18n.tr.userData.newEmail} bind:value={new_email}/>
        <Input id="change-email-confirm" type="email" placeholder={i18n.tr.userData.newEmailConfirm} bind:value={new_email_repeat}/>
        <Button size="lg" type="submit">{i18n.tr.userData.changeEmail}</Button>
	</form>

    {#if showSuccessMail}
        <div class = "pb-2 mb-2">
            <CheckCircleSolid size ="xl" class = "text-feedback-0 px-2 mx-2"/>
            <span >{i18n.tr.userData.confirmChangeSuccess}</span>
        </div>
    {/if}

    <form class = "space-y-4 mb-2 pb-2" onsubmit={preventDefault(submitNewPassword)}>
        <Label
            for={"new_password"}
            class="font-semibold text-gray-700 dark:text-gray-400"
        >{i18n.tr.userData.changePassword}</Label>
        <Input
            bind:value={new_password}
            type="password"
            id="new_password"
            placeholder={i18n.tr.userData.newPassword}
        />

        <Label
            for={"new_password-confirm"}
            class="font-semibold text-gray-700 dark:text-gray-400"
        >{i18n.tr.userData.newPasswordConfirm}</Label>
        <Input
            bind:value={new_password_repeat}
            type="password"
            id="new_password-confirm"
            placeholder={i18n.tr.userData.newPasswordConfirm}
        />
        <Button size="lg" type="submit">{i18n.tr.userData.changePassword}</Button>
    </form>

    {#if showSuccessPassword}
        <div class = "pb-2 mb-2">
            <CheckCircleSolid size ="xl" class = "text-feedback-0 px-2 mx-2"/>
            <span >{i18n.tr.userData.confirmChangeSuccess}</span>
        </div>
    {/if}
</div>
