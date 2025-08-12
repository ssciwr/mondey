<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import { type ResetForgotPasswordData, resetForgotPassword } from "$lib/client";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input } from "flowbite-svelte";

const maildata = {
	component: "input",
	type: "email",
	props: {
		placeholder: i18n.tr.forgotPw.placeholder,
		id: "email",
		required: true,
	},
};

let userEmail = $state("");
let confirmEmail = $state("");

let showSuccess = $state(false);

async function submitData(): Promise<void> {
	if (userEmail !== confirmEmail) {
		alertStore.showAlert(
			i18n.tr.forgotPw.alertTitle,
			i18n.tr.forgotPw.confirmError,
			true,
			false,
		);
		return;
	}

	const data: ResetForgotPasswordData = {
		body: {
			email: userEmail,
		},
	};
	const response = await resetForgotPassword(data);

	if (response.error) {
		console.log("error: ", response.error);
		let errorMessage = i18n.tr.forgotPw.sendError;
		if (response.response?.status === 422) {
			errorMessage = i18n.tr.login.badData;
		}
		alertStore.showAlert(
			i18n.tr.forgotPw.alertTitle,
			errorMessage,
			true,
			false,
		);
	} else {
		console.log("successful transmission of forgot password email");
		console.log("response: ", response);
		showSuccess = true;
	}
}
</script>


<Card class="container m-2 mx-auto w-full max-w-xl items-center justify-center p-2">
	<Heading
		tag="h3"
		class="m-2 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{i18n.tr.forgotPw.heading}</Heading
	>
	{#if showSuccess === false}
		<form onsubmit={preventDefault(submitData)}>
			<div class="m-2 mx-auto w-full flex-col space-y-6 p-2">
				<DataInput
					component={maildata.component}
					bind:value={userEmail}
					{...maildata.props}
				/>
				<DataInput
					component={maildata.component}
					bind:value={confirmEmail}
					{...maildata.props}
				/>
			</div>

			<div class="m-2 flex w-full items-center justify-center p-2">
				<Button size="md" type="submit">{i18n.tr.forgotPw.pending}</Button>
			</div>
		</form>
	{:else}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<Button
				class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				size="md"
				type="button"
				on:click={(event) => {
					goto(`/${base}`);
				}}>{i18n.tr.forgotPw.success}</Button
			>
		</div>
	{/if}
</Card>
