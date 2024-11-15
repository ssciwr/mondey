<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";

import { type ResetForgotPasswordData } from "$lib/client";
import { resetForgotPassword } from "$lib/client/services.gen";
import { preventDefault } from "$lib/util";

import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { Button, Card, Heading, Input } from "flowbite-svelte";
import { _ } from "svelte-i18n";

const maildata = {
	component: Input,
	type: "email",
	value: "",
	props: {
		placeholder: $_("forgotPw.placeholder"),
		id: "email",
		required: true,
	},
};

let alertMessage: string = $_("forgotPw.formatError");
let showAlert: boolean;
let showSuccess = false;

async function submitData(): Promise<void> {
	const data: ResetForgotPasswordData = {
		body: {
			email: maildata.value,
		},
	};

	const result = await resetForgotPassword(data);

	if (result.error) {
		console.log("error: ", result.error);
		showAlert = true;
		alertMessage = $_("forgotPw.sendError");
	} else {
		console.log(
			"successful transmission, response status: ",
			result.response.status,
		);
		showSuccess = true;
	}
}
</script>

{#if showAlert}
	<AlertMessage
		title={$_('forgotPw.alertTitle')}
		message={alertMessage}
		lastpage={`${base}/userLand/lostPassword`}
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
					bind:value={maildata.value}
					{...maildata.props}
				/>
			</div>

			<div class="m-2 flex w-full items-center justify-center p-2">
				<Button size="md" type="submit">{$_('forgotPw.pending')}</Button>
			</div>
		</form>
	{:else}
		<div class="m-2 flex w-full items-center justify-center p-2">
			<p>{$_('forgotPw.mailSentMessage')}</p>
		</div>
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
