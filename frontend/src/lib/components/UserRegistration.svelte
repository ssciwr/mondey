<script lang="ts">
import { base } from "$app/paths";
import { registerRegister } from "$lib/client/services.gen";
import { type RegisterRegisterData } from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input, Select } from "flowbite-svelte";
import { _ } from "svelte-i18n";

async function submitData(): Promise<void> {
	const equalPW = data[1].value !== "" && data[2].value === data[1].value;

	const userData: RegisterRegisterData = {
		body: {
			email: "",
			password: "",
			is_active: false,
			is_superuser: false,
			is_researcher: false,
		},
	};
	if (equalPW) {
		userData.body.email = data[0].value;
		userData.body.password = data[1].value;
		userData.body.is_researcher =
			data[3].value === $_("registration.researcherRole");
		userData.body.is_superuser = data[3].value === $_("registration.adminRole");
		userData.body.is_active = true;

		const result = await registerRegister(userData);

		if (result.error) {
			console.log("error: ", result.response.status, result.error.detail);
			alertMessage =
				$_("registration.alertMessageError") + ": " + result.error.detail;
			showAlert = true;
		} else {
			console.log("successful transmission: ", result.response.status);
			success = true;
		}
		data.forEach((element) => {
			element.value = "";
		});
	} else {
		showAlert = true;
		alertMessage = $_("registration.alertMessagePasswords");
	}
}

const data = [
	{
		component: Input,
		props: {
			label: $_("registration.emailLabel"),
			type: "email",
			placeholder: $_("registration.emailLabel"),
			required: true,
			id: "email",
		},
		value: "",
	},
	{
		component: Input,
		props: {
			label: $_("registration.passwordLabel"),
			type: "password",
			placeholder: $_("registration.passwordLabel"),
			required: true,
			id: "password",
		},
		value: "",
	},
	{
		component: Input,
		props: {
			label: $_("registration.passwordConfirmLabel"),
			type: "password",
			placeholder: $_("registration.passwordConfirmLabel"),
			required: true,
			id: "passwordConfirm",
		},
		value: "",
	},
	{
		component: Select,
		props: {
			label: $_("registration.role"),
			type: "text",
			placeholder: $_("registration.selectPlaceholder"),
			required: true,
			id: "role",
			items: [
				$_("registration.observerRole"),
				$_("registration.researcherRole"),
				$_("registration.adminRole"),
			].map((v) => {
				return { name: String(v), value: v };
			}),
		},
		value: $_("registration.observerRole"),
	},
];

let showAlert = false;
let success = false;
let alertMessage = $_("registration.alertMessageMissing");
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('registration.alertMessageTitle')}
		message={alertMessage}
		infopage="{base}/info"
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
		>{$_('registration.heading')}
	</Heading>

	{#if success === false}
		<form onsubmit={preventDefault(submitData)} class="m-2 mx-auto w-full flex-col space-y-6">
			{#each data as element, i}
				<DataInput
					component={element.component}
					properties={element.props}
					bind:value={element.value}
					eventHandlers={{
						'on:change': element.onChange,
						'on:blur': element.onBlur,
						'on:click': element.onClick
					}}
					label={element.props.label}
				/>
			{/each}

			<Button
				type="submit"
				class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
				>{$_('registration.submitButtonLabel')}</Button
			>
		</form>
	{:else}
		<UserVerify />
	{/if}
</Card>
