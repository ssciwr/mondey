<script lang="ts">
	import { base } from '$app/paths';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading, Input } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';


	const data = [
		{
			component: Input,
			props: {
				label: $_('registration.usernameLabel'),
				type: 'text',
				placeholder: $_('registration.usernameLabel'),
				required: true,
				id: 'username'
			},
			value: ''
		},
		{
			component: Input,
			props: {
				label:  $_('registration.emailLabel'),
				type: 'email',
				placeholder: $_('registration.emailLabel'),
				required: true,
				id: 'email'
			},
			value: ''
		},
		{
			component: Input,
			props: {
				label: $_('registration.passwordLabel'),
				type: 'password',
				placeholder: $_('registration.passwordLabel'),
				required: true,
				id: 'password'
			},
			value: ''

		},
		{
			component: Input,
			props: {
				label: $_('registration.passwordConfirmLabel'),
				type: 'password',
				placeholder: $_('registration.passwordConfirmLabel'),
				required: true,
				id: 'passwordConfirm'
			},
			value: ''
		}
	];

	let showAlert: boolean = false;

</script>

<!-- Show big alert message when something is missing -->
{#if showAlert}
	<AlertMessage
		title={$_('registration.alertMessageTitle')}
		message={$_('registration.alertMessage')}
		infopage="{base}/info"
		infotitle="Was passiert mit den Daten"
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
			>{$_('registration.heading')}
		</Heading>

		<form onsubmit={preventDefault((e) => {
			console.log('event: ', e);
		})} class="m-2 mx-auto w-full flex-col space-y-6">

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
			class="dark:bg-primay-700 bg-primary-700 hover:bg-primary-800 dark:hover:bg-primary-800 w-full text-center text-sm text-white hover:text-white"
			>{$_('registration.submitButtonLabel')}</Button>
		</form>
	</Card>
</div>
