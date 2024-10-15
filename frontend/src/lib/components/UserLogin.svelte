<script lang="ts">
	import { base } from '$app/paths';

	import UserLoginUtil from '$lib/components//UserLoginUtil.svelte';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';

	import { goto } from '$app/navigation';
	import { authCookieLogin } from '$lib/client';
	import {
		type AuthCookieLoginData,
		type Body_auth_cookie_login_auth_login_post
	} from '$lib/client/types.gen';
	import { preventDefault } from '$lib/util';
	import { Button, Card, Heading, Input, Select } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';

	// functionality
	async function submitData() {
		const loginData: Body_auth_cookie_login_auth_login_post = {
			username: formData[0].value,
			password: formData[1].value
		};

		const data: AuthCookieLoginData = {
			body: loginData
		};

		const authReturn = await authCookieLogin(data);

		if (authReturn.error) {
			showAlert = true;
			for (let element of formData) {
				element.value = '';
			}
		} else {
			goto('/userLand/userLandingpage');
		}
	}

	// form data and variables
	let formData = [
		{
			component: Input,
			value: '',
			props: {
				label: $_('login.usernameLabel'),
				type: 'text',
				placeholder: $_('login.usernameLabel'),
				required: true,
				id: 'username'
			}
		},
		{
			component: Input,
			value: '',
			props: {
				label: $_('login.passwordLabel'),
				type: 'password',
				placeholder: $_('login.passwordLabel'),
				required: true,
				id: 'password'
			}
		},
		{
			component: Select,
			value: '',
			props: {
				label: $_('login.role'),
				items: [$_('login.observerRole'), $_('login.scientistRole'), $_('login.adminRole')].map(
					(v) => {
						return { name: String(v), value: v };
					}
				),
				placeholder: $_('login.selectPlaceholder'),
				required: true,
				id: 'role'
			}
		}
	];

	let remember: boolean = false;
	let showAlert: boolean = false;
	$: console.log('remember: ', remember, 'showAlert: ', showAlert);
</script>

{#if showAlert}
	<AlertMessage
		title={$_('login.alertMessageTitle')}
		message={$_('login.alertMessage')}
		lastpage={`${base}/userLand/userLogin`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

<!-- {#if users.get()['loggedIn'] && users.get()['loggedIn'] !== null}
	<AlertMessage
		title={$_('login.alertMessageTitle')}
		message={$_('login.alreadyLoggedInMessage')}
		lastpage={`${base}`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{:else} -->
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
				class="dark:bg-primay-700 bg-primary-700 hover:bg-primary-800 dark:hover:bg-primary-800 w-full text-center text-sm text-white hover:text-white"
				type="submit">{$_('login.submitButtonLabel')}</Button
			>
		</form>
	</Card>

	<span class="container mx-auto w-full text-gray-700 dark:text-gray-400">Not registered?</span>
	<a
		href={`${base}/userLand/userRegistration`}
		class="text-primary-700 dark:text-primary-500 hover:underline"
	>
		Create account
	</a>
</div>
<!-- {/if} -->
