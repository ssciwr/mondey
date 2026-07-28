<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";

import { alertStore } from "$lib/stores/alertStore.svelte";

import { goto } from "$app/navigation";
import { verifyRequestToken } from "$lib/client/sdk.gen";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { preventDefault } from "$lib/util";
import { Alert, Button, Card, Heading, Input, Label } from "flowbite-svelte";

import { page } from "$app/state";

// functionality
async function submitData(): Promise<void> {
	notVerified = false;
	activationEmailSent = false;
	const authReturn = await user.login({
		username: username,
		password: password,
	});
	if (authReturn.error) {
		// The account exists and the password is correct, but the email address was
		// never activated. Say so, rather than claiming the credentials are wrong.
		if (authReturn.error.detail === "LOGIN_USER_NOT_VERIFIED") {
			notVerified = true;
		} else {
			alertStore.showAlert(
				i18n.tr.login.alertMessageTitle,
				i18n.tr.login.badCredentials,
				true,
				false,
			);
		}
		console.log("error during login ", authReturn.error.detail);
	} else {
		await user.load();
		if (user.data === null) {
			console.log("error retrieving active user");
			alertStore.showAlert(
				i18n.tr.login.alertMessageTitle,
				i18n.tr.login.unauthorized,
				true,
				false,
			);
		} else {
			const intendedPath = page.url.searchParams.get("intendedpath");
			if (intendedPath !== null && intendedPath.length > 2) {
				console.log("Redirecting user to intended path: ", intendedPath);
				goto(intendedPath);
			} else {
				goto("/userLand/children");
			}
		}
	}
}

async function resendActivationEmail(): Promise<void> {
	sendingActivationEmail = true;
	const { error } = await verifyRequestToken({ body: { email: username } });
	sendingActivationEmail = false;
	if (error) {
		console.log("error requesting activation email ", error);
		alertStore.showAlert(
			i18n.tr.login.alertMessageTitle,
			i18n.tr.login.resendActivationError,
			true,
			false,
		);
		return;
	}
	activationEmailSent = true;
}

// form data and variables

let username = $state("");
let password = $state("");
let notVerified = $state(false);
let sendingActivationEmail = $state(false);
let activationEmailSent = $state(false);
</script>


<div class="container m-2 mx-auto w-full max-w-xl p-6">
	<Card class="container m-2 mx-auto mb-6 w-full max-w-xl pb-6">
		<Heading
			tag="h3"
			class="m-2 mb-3 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
			>{i18n.tr.login.heading}</Heading
		>

		<form
			onsubmit={preventDefault(submitData)}
			class="m-2 mx-auto w-full flex-col space-y-6"
		>
			<div class="space-y-4">
				<Label
					for={"username"}
					class="font-semibold text-gray-700 dark:text-gray-400"
					>{i18n.tr.login.usernameLabel}</Label
				>
				<Input
					type="email"
					bind:value={username}
					autocomplete="username"
					id="username"
					placeholder={i18n.tr.login.usernameLabel}
					required
				/>
			</div>
			<div class="space-y-4">
				<Label
					for={"password"}
					class="font-semibold text-gray-700 dark:text-gray-400"
					>{i18n.tr.login.passwordLabel}</Label
				>
				<Input
					type="password"
					bind:value={password}
					autocomplete="current-password"
					id="password"
					placeholder={i18n.tr.login.passwordLabel}
					required
				/>
				<a href={`${base}/forgotPassword`} class="text-primary-700 dark:text-primary-500">
					{i18n.tr.login.forgotPassword} </a>
			</div>

			<Button
				class="dark:bg-primary-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				type="submit">{i18n.tr.login.submitButtonLabel}</Button
			>
		</form>

		{#if notVerified}
			<Alert color="yellow" class="m-2" id="notVerifiedAlert">
				<span class="font-semibold">{i18n.tr.login.notVerifiedTitle}</span>
				<p class="mt-1">{i18n.tr.login.notVerifiedMessage}</p>
				{#if activationEmailSent}
					<p class="mt-3 font-semibold" id="activationEmailSent">
						{i18n.tr.login.resendActivationSent}
					</p>
				{:else}
					<Button
						id="resendActivationButton"
						class="mt-3"
						size="sm"
						disabled={sendingActivationEmail}
						on:click={resendActivationEmail}
						>{i18n.tr.login.resendActivation}</Button
					>
				{/if}
			</Alert>
		{/if}
	</Card>

	<span class="container mx-auto w-full text-gray-700 dark:text-gray-400"
		>{i18n.tr.login.notRegistered}</span
	>
	<a
		href={`${base}/signup`}
		class="text-primary-700 hover:underline dark:text-primary-500"
	>
		{i18n.tr.login.registerNew}
	</a>
</div>
