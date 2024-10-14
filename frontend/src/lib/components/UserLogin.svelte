<script lang="ts">
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';

	import UserLoginUtil from '$lib/components//UserLoginUtil.svelte';
	import AlertMessage from '$lib/components/AlertMessage.svelte';
	import DataInput from '$lib/components/DataInput/DataInput.svelte';
	import NavigationButtons from '$lib/components/Navigation/NavigationButtons.svelte';

	import { hash, users, type UserData } from '$lib/stores/userStore';
	import { Card, Heading } from 'flowbite-svelte';
	import { onDestroy, onMount } from 'svelte';

	// functionality

	/**
	 * This currently immitates the behavior of a login system by fetching data from
	 * the userstore that has been precreated. What fetchWithCredentials does currently will later go into the backend
	 */
	async function validateCredentials() {
		// README: this should not be set here but in the child component. However, indication of something missing should
		// not happen immediatelly in the first round of entry, so this code here defers it until the first hit of the login button.

		const user = await users.fetchWithCredentials(
			data[0].value,
			await hash(data[1].value),
			data[2].value
		);

		console.log(user);

		if (user) {
			userID = user.id;

			if (remember) {
				localStorage.setItem('currentUser', JSON.stringify(userID));
			} else {
				localStorage.removeItem('currentUser');
			}

			await users.setLoggedIn(userID);

			await users.save();

			goto(`${base}/userLand/userLandingpage/`);
		} else {
			showAlert = true;
			data = data.map((element) => {
				element.value = null;
				return element;
			});
		}
	}

	// data and variables
	export let data: any[];

	const buttons = [
		{
			label: 'Login',
			href: null,
			onclick: validateCredentials
		}
	];

	let alertMessage = 'Eingaben sind falsch';
	let userID: string;
	let remember: boolean = false;
	let showAlert: boolean = false;
	const heading = 'Einloggen';

	// check if credentials are stored
	onMount(async () => {
		// make dummyUser if not already there
		users.load();

		// check if credentials are saved
		const savedUID = JSON.parse(localStorage.getItem('currentUser'));

		if (savedUID) {
			userID = savedUID;

			const user: UserData = (await users.fetch(userID)) as UserData;

			data[0].value = user.name;
			data[1].value = user.password;
			data[2].value = user.role;
			remember = true;
		}
	});

	onDestroy(async () => {
		await users.save();
	});
</script>

{#if showAlert}
	<AlertMessage
		title={'Fehler'}
		message={alertMessage}
		lastpage={`${base}/userLand/userLogin`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}

{#if users.get()['loggedIn'] && users.get()['loggedIn'] !== null}
	<AlertMessage
		title={'Fehler'}
		message={`Sie sind bereits angemeldet. Melden sie sich zuerst ab um den Account zu wechseln.`}
		lastpage={`${base}`}
		onclick={() => {
			showAlert = false;
		}}
	/>
{:else}
	<div class="container m-1 mx-auto w-full max-w-xl">
		<Card class="container m-1 mx-auto mb-6 w-full max-w-xl pb-6">
			{#if heading}
				<Heading
					tag="h3"
					class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
					>{heading}</Heading
				>
			{/if}

			<form class="m-1 m-3 mx-auto w-full flex-col space-y-6">
				{#each data as element}
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
			</form>

			<UserLoginUtil cls="p-6 mb-3" bind:checked={remember} />

			<NavigationButtons {buttons} />
		</Card>

		<span class="container mx-auto w-full text-gray-700 dark:text-gray-400">Not registered?</span>
		<a
			href={`${base}/userLand/userRegistration`}
			class="text-primary-700 hover:underline dark:text-primary-500"
		>
			Create account
		</a>
	</div>
{/if}
