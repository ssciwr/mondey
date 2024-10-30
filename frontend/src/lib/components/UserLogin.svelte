<script lang="ts">
import { base } from "$app/paths";

import UserLoginUtil from "$lib/components//UserLoginUtil.svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";

import { goto } from "$app/navigation";
import { authCookieLogin, usersCurrentUser } from "$lib/client/services.gen";
import { type AuthCookieLoginData, type UserRead } from "$lib/client/types.gen";
import { currentUser } from "$lib/stores/userStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input } from "flowbite-svelte";
import { _ } from "svelte-i18n";

async function refresh(): Promise<string> {
	const returned = await usersCurrentUser();
	if (returned.error) {
		console.log("Error getting current user: ", returned.error.detail);
		currentUser.set(null);
		return returned.error.detail;
	} else {
		console.log("Successfully retrieved active user");
		currentUser.set(returned.data as UserRead);
		return "success";
	}
}

// functionality
async function submitData(): Promise<void> {
	const loginData: AuthCookieLoginData = {
		body: {
			username: formData[0].value,
			password: formData[1].value,
		},
	};

	const authReturn = await authCookieLogin(loginData);

	// forget user data again to not have a plain text password lying around in memory somewhere
	// any longer than needed

	if (authReturn.error) {
		showAlert = true;
	} else {
		const status: string = await refresh();

		if (status !== "success") {
			console.log("error during retrieving active users: ", status);
			showAlert = true;
			alertMessage = $_("login.unauthorized") + ": " + status;
		} else {
			console.log("login and user retrieval successful");
			goto("/userLand/userLandingpage");
		}
	}
}

// form data and variables
let formData = [
	{
		component: Input,
		value: "",
		props: {
			label: $_("login.usernameLabel"),
			type: "email",
			placeholder: $_("login.usernameLabel"),
			required: true,
			id: "username",
			autocomplete: "username",
		},
	},
	{
		component: Input,
		value: "",
		props: {
			label: $_("login.passwordLabel"),
			type: "password",
			placeholder: $_("login.passwordLabel"),
			required: true,
			id: "password",
			autocomplete: "password",
		},
	},
];

let remember = false;
let showAlert = false;
let alertMessage: string = $_("login.badCredentials");
</script>

{#if showAlert}
	<AlertMessage
		title={$_('login.alertMessageTitle')}
		message={alertMessage}
		lastpage={`${base}/userLand/userLogin`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<div class="container m-2 mx-auto w-full max-w-xl">
	<Card class="container m-2 mx-auto mb-6 w-full max-w-xl pb-6">
		<Heading
			tag="h3"
			class="m-2 mb-3 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
			>{$_('login.heading')}</Heading
		>

		<form onsubmit={preventDefault(submitData)} class="m-2 mx-auto w-full flex-col space-y-6">
			{#each formData as element}
				<DataInput
					component={element.component}
					label={element.props.label}
					bind:value={element.value}
					properties={element.props}
					eventHandlers={{
						'on:change': element.onchange,
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
				/>
			{/each}

			<UserLoginUtil cls="p-6 mb-3" bind:checked={remember} />

			<Button
				class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				type="submit">{$_('login.submitButtonLabel')}</Button
			>
		</form>
	</Card>

	<span class="container mx-auto w-full text-gray-700 dark:text-gray-400">Not registered?</span>
	<a
		href={`${base}/userLand/userRegistration`}
		class="text-primary-700 hover:underline dark:text-primary-500"
	>
		Create account
	</a>
</div>
