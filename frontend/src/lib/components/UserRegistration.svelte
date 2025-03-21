<script lang="ts">
import { registerRegister } from "$lib/client/services.gen";
import { type RegisterRegisterData } from "$lib/client/types.gen";
import ResearchCodeInput from "$lib/components/DataInput/ResearchCodeInput.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input, Label } from "flowbite-svelte";

async function submitData(): Promise<void> {
	if (user.data) {
		// if anonymous test account or otherwise logged in, log them out first.
		await user.logout();
	}

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
		alertStore.showAlert(
			i18n.tr.registration.alertMessageTitle,
			`${i18n.tr.registration.alertMessageError}: ${result.error.detail} ${i18n.tr.registration.infoTitle}`,
			true,
			false,
		);
	} else {
		console.log("successful transmission: ", result.response.status);
		success = true;
	}
}

let email = $state("");
let password = $state("");
let passwordConfirm = $state("");
let success = $state(false);
let researchCodeValid = $state(false);
let passwordValid = $derived(password !== "" && password === passwordConfirm);

let { researchCode = "" }: { researchCode?: string } = $props();
</script>


<!-- The actual content -->
<Card class="container m-2 mx-auto w-full max-w-xl p-2">
	<Heading
		tag="h3"
		class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{i18n.tr.registration.heading}
	</Heading>

	{#if success === false}
		<form
			onsubmit={preventDefault(submitData)}
			class="m-2 mx-auto w-full flex-col space-y-6"
		>
			<Label
				for={"username"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{i18n.tr.registration.emailLabel}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={email}
					required
					type="email"
					id="email"
					autocomplete="email"
					placeholder={i18n.tr.registration.emailLabel}
				/>
			</div>

			<Label
				for={"password"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{i18n.tr.registration.passwordLabel}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={password}
					required
					type="password"
					id="password"
					autocomplete="new-password"
					placeholder={i18n.tr.registration.passwordLabel}
				/>
			</div>

			<Label
				for={"password_confirm"}
				class="font-semibold text-gray-700 dark:text-gray-400"
				>{i18n.tr.registration.passwordConfirmLabel}</Label
			>
			<div class="space-y-4">
				<Input
					bind:value={passwordConfirm}
					required
					type="password"
					id="passwordConfirm"
					autocomplete="new-password"
					placeholder={i18n.tr.registration.passwordConfirmLabel}
					color={passwordConfirm === password ? 'base' : 'red'}
				/>
			</div>

			<Label class="font-semibold text-gray-700 dark:text-gray-400">{i18n.tr.registration.researchCode}</Label>
			<ResearchCodeInput bind:value={researchCode} bind:valid={researchCodeValid}></ResearchCodeInput>

			<Button
				type="submit"
				disabled={!(researchCodeValid && passwordValid)}
				class="dark:bg-primary-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				>{i18n.tr.registration.submitButtonLabel}</Button
			>
		</form>
	{:else}
		<UserVerify />
	{/if}
</Card>
