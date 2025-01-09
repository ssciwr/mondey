<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import { type ResetForgotPasswordData, resetForgotPassword } from "$lib/client";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input } from "flowbite-svelte";
import { _ } from "svelte-i18n";

const maildata = {
	component: Input,
	type: "email",
	props: {
		placeholder: $_("forgotPw.placeholder"),
		id: "email",
		required: true,
	},
};

let userEmail = $state("");
let confirmEmail = $state("");

let alertMessage: string = $state($_("forgotPw.formatError"));
let showAlert: boolean = $state(false);
let showSuccess = $state(false);

async function submitData(): Promise<void> {
	if (userEmail !== confirmEmail) {
		alertMessage = $_("forgotPw.confirmError");
		showAlert = true;
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
		alertMessage = $_("forgotPw.sendError");
		showAlert = true;
	} else {
		console.log("successful transmission of forgot password email");
		console.log("response: ", response);
		showSuccess = true;
	}
}
</script>

{#if showAlert}
	<AlertMessage
		title={$_('forgotPw.alertTitle')}
		message={alertMessage}
		lastpage={`${base}/forgotPassword`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<Card class="container m-2 mx-auto w-full max-w-xl items-center justify-center p-2">
	<Heading
		tag="h3"
		class="m-2 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
		>{$_('forgotPw.heading')}</Heading
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
				<Button size="md" type="submit">{$_('forgotPw.pending')}</Button>
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
				}}>{$_('forgotPw.success')}</Button
			>
		</div>
	{/if}
</Card>
