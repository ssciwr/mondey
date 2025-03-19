<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";

import AlertMessage from "$lib/components/AlertMessage.svelte";

import { goto } from "$app/navigation";
import { authCookieLogin, usersCurrentUser } from "$lib/client/services.gen";
import { type AuthCookieLoginData } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input, Label } from "flowbite-svelte";

async function refresh(): Promise<string> {
	const returned = await usersCurrentUser();
	if (returned.error) {
		user.data = null;
		console.log("Error getting current user: ", returned.error.detail);
		return returned.error.detail;
	}
	console.log("Successfully retrieved active user");
	if (returned.data === null || returned.data === undefined) {
		user.data = null;
		return "no user data";
	}
	user.data = returned.data;
	return "success";
}

// functionality
async function submitData(): Promise<void> {
	const loginData: AuthCookieLoginData = {
		body: {
			username: username,
			password: password,
		},
	};

	const authReturn = await authCookieLogin(loginData);

	if (authReturn.error) {
		showAlert = true;
		alertMessage = i18n.tr.login.badCredentials + authReturn.error.detail;
		console.log("error during login ", authReturn.error.detail);
	} else {
		const status: string = await refresh();
		if (status !== "success") {
			console.log("error during retrieving active users: ", status);
			showAlert = true;
			alertMessage = `${i18n.tr.login.unauthorized}: ${status}`;
		} else {
			console.log("login and user retrieval successful");
			goto("/userLand/children/gallery");
		}
	}
}

// form data and variables

let username = $state("");
let password = $state("");
let showAlert = $state(false);
let alertMessage: string = $state(i18n.tr.login.badCredentials);
</script>

{#if showAlert}
	<AlertMessage
		title={i18n.tr.login.alertMessageTitle}
		message={alertMessage}
		lastpage={`${base}/login`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

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
				class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				type="submit">{i18n.tr.login.submitButtonLabel}</Button
			>
		</form>
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
