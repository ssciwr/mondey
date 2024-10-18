<script lang="ts">
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading } from 'flowbite-svelte';
	import { CheckCircleOutline } from 'flowbite-svelte-icons';
	import { _ } from 'svelte-i18n';

	import {} from '$lib/client/services.gen';

	// TODO: As researcher, you don´t have to provide these data. Researchers have another component that is all there own and does not yet exist. Hence, the userlandingpage should not have this component

	// TODO: not sure this is good.... seems like a lot of logic and work to do here...
	function checkDataFilled(values: any[]) {
		console.log('checkfilled: ', values);
		let allFilled = true;
		for (const element of values) {
			console.log('  element: ', element);
			allFilled = allFilled && element !== null && element !== '' && element !== undefined;
		}
		console.log('all done: ', allFilled);
		return allFilled;
	}

	async function submitData() {
		const error: Error | null = null;
		// TODO: call the respective API function here to update the data
		done = true;

		if (error) {
			showAlert = true;
			alertMessage = $_('userData.alertMessageError') + ': ' + error.detail;
		}
	}

	// this can, but does not have to, come from a database later.
	// TODO: this needs to load data from the backend
	export let data: any[];

	let showAlert: boolean = false;
	let done: boolean = checkDataFilled(
		data.map((element) => {
			return element.value;
		})
	);
	let alertMessage = $_('userData.alertMessageMissing');
</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('userData.alertMessageTitle')}
		message={alertMessage}
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
					disabled={done}
					eventHandlers={{
						'on:change': (e) => {
							if (element.onchange) {
								element.onchange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
					additionalEventHandlers={{
						'on:change': (e) => {
							if (element.additionalOnChange) {
								element.additionalOnChange(e);
							}
						},
						'on:blur': element.onblur,
						'on:click': element.onclick
					}}
				/>
			{/each}
			{#if done}
				<div
					class="m-2 flex w-full items-center justify-center p-2 text-gray-700 dark:text-gray-400"
				>
					<CheckCircleOutline size="xl" color="green" class="" />
					{$_('userData.submitSuccessMessage')}
				</div>

				<Button
					type="button"
					class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
					on:click={(e) => {
						done = false;
					}}>{$_('userData.changeButtonLabel')}</Button
				>
			{:else}
				<Button
					class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
					type="submit">{$_('userData.submitButtonLabel')}</Button
				>
			{/if}
		</form>
	</Card>
</div>
