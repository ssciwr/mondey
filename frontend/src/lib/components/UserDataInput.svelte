<script lang="ts">
	import { goto } from '$app/navigation';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { users, type UserData } from '$lib/stores/userStore';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';

	function validate(): boolean {
		missingValues = data.map((element) => element.value === '' || element.value === null);
		return missingValues.every((v) => v === false);
	}

	async function submitData() {
		const valid = validate();
		if (valid) {
			for (let i = 0; i < data.length; ++i) {
				(userData as UserData)[data[i].props.name] = {};
				(userData as UserData)[data[i].props.name]['value'] = data[i].value;
				(userData as UserData)[data[i].props.name]['additionalValue'] = data[i].additionalValue;
			}

			if (userID) {
				await users.update(userID, userData);
			}

			await users.save();

			buttons[0].disabled = true;
			showAlert = false;
			goto('/userLand/userLandingpage');
		} else {
			showAlert = true;
		}
	}

	let userData: UserData;
	let userID: string;

	// this can, but does not have to, come from a database later.
	export let data: any[];

	let missingValues = data.map(() => false);

	let showAlert: boolean = true;

	let alertMessage: string = 'Bitte füllen Sie die benötigten Felder (hervorgehoben) aus.';

	const buttons = [
		{
			label: 'Abschließen',
			onclick: submitData,
			disabled: true
		}
	];
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('userData.alertMessageTitle')}
		message={$_('userData.alertMessageMissing')}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- The actual content -->
<div class="container m-1 mx-auto w-full max-w-xl">
	<Card class="container m-1 mx-auto w-full max-w-xl">
		<Heading
			tag="h3"
			class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
			>{$_('userData.heading')}</Heading
		>

		<form class="m-1 mx-auto w-full flex-col space-y-6" onsubmit={preventDefault(submitData)}>
			{#each data as element, i}
				<DataInput
					component={element.component}
					bind:value={element.value}
					bind:additionalInput={element.additionalValue}
					label={element.props.label}
					properties={element.props}
					textTrigger={element.props.textTrigger}
					eventHandlers={{
						'on:change': (e) => {
							buttons[0].disabled = false;
							if (element.onchange) {
								element.onchange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
					additionalEventHandlers={{
						'on:change': (e) => {
							buttons[0].disabled = false;
							if (element.additionalOnChange) {
								element.additionalOnChange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
				/>
			{/each}
		</form>
		<Button
			class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
			type="submit">{$_('userData.submitButtonLabel')}</Button
		>
	</Card>
</div>
