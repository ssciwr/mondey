<script lang="ts">
import { registerRegister } from "$lib/client/services.gen";
import { type RegisterRegisterData } from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import ResearchCodeInput from "$lib/components/DataInput/ResearchCodeInput.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input, Label } from "flowbite-svelte";
import { _ } from "svelte-i18n";

async function submitData(): Promise<void> {
	const userData: RegisterRegisterData = {
		body: {
			email: email,
			password: password,
			is_active: true,
			research_group_id: Number(researchCode),
		},
	};
	const result = await registerRegister(userData);

	if (result.error) {
		console.log("error: ", result.response.status, result.error.detail);
		alertMessage = `${$_("registration.alertMessageError")}: ${result.error.detail}`;
		showAlert = true;
	} else {
		console.log("successful transmission: ", result.response.status);
		success = true;
	}
}

let email = $state("");
let password = $state("");
let passwordConfirm = $state("");
let showAlert = $state(false);
let success = $state(false);
let alertMessage = $state($_("registration.alertMessageMissing"));
let researchCodeValid = $state(false);
let passwordValid = $derived(password !== "" && password === passwordConfirm);

let { researchCode = "" }: { researchCode?: string } = $props();
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_("registration.alertMessageTitle")}
		message={alertMessage}
		infotitle="Was passiert mit den Daten"
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- The actual content -->
<Card class="container m-2 mx-auto w-full max-w-xl p-2">
	<Heading
		tag="h3"
		class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{$_("registration.heading")}
	</Heading>

	{#if success === false}
		<form
			onsubmit={preventDefault(submitData)}
			class="m-2 mx-auto w-full flex-col space-y-6"
		>
			<Label
				for={"username"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_("registration.emailLabel")}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={email}
					required
					type="email"
					id="email"
					autocomplete="email"
					placeholder={$_("registration.emailLabel")}
				/>
			</div>

			<Label
				for={"password"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_("registration.passwordLabel")}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={password}
					required
					type="password"
					id="password"
					autocomplete="new-password"
					placeholder={$_("registration.passwordLabel")}
				/>
			</div>

			<Label
				for={"password_confirm"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{$_("registration.passwordConfirmLabel")}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={passwordConfirm}
					required
					type="password"
					id="passwordConfirm"
					autocomplete="new-password"
					placeholder={$_("registration.passwordConfirmLabel")}
					color={passwordConfirm === password ? 'base' : 'red'}
				/>
			</div>

			<Label class="font-semibold text-gray-700 dark:text-gray-400">{$_("registration.researchCode")}</Label>
			<ResearchCodeInput bind:value={researchCode} bind:valid={researchCodeValid}></ResearchCodeInput>

			<Button
				type="submit"
				disabled={!(researchCodeValid && passwordValid)}
				class="dark:bg-primary-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				>{$_("registration.submitButtonLabel")}</Button
			>
		</form>
	{:else}
		<UserVerify />
	{/if}
</Card>
