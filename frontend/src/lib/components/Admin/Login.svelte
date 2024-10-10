<svelte:options runes={true} />

<script lang="ts">
	import { Input, Label, Button, Card, Alert } from 'flowbite-svelte';
	import { adminUser } from '$lib/admin.svelte';
	import { preventDefault } from '$lib/util';
	import type { Body_auth_cookie_login_auth_login_post } from '$lib/client/types.gen';
	import { _ } from 'svelte-i18n';

	const loginData: Body_auth_cookie_login_auth_login_post = { username: '', password: '' };
	let errorCode = $state('');

	async function doLogin() {
		errorCode = await adminUser.login(loginData);
	}
</script>

<Card size="lg">
	<h5 class="mb-5 text-center text-2xl font-bold text-gray-900 dark:text-white">Admin login</h5>
	<div class="mb-5">
		<form onsubmit={preventDefault(doLogin)}>
			<div class="mb-6">
				<Label for="email" class="mb-2">Email address</Label>
				<Input
					type="email"
					bind:value={loginData.username}
					id="email"
					placeholder="john.doe@company.com"
					required
					autocomplete="username"
				/>
			</div>
			<div class="mb-6">
				<Label for="password" class="mb-2">Password</Label>
				<Input
					type="password"
					bind:value={loginData.password}
					id="password"
					placeholder="•••••••••"
					required
					autocomplete="current-password"
				/>
			</div>
			<Button type="submit" class="mb-6">Login</Button>
			{#if errorCode !== ''}
				<Alert>{$_(`login.${errorCode}`)}</Alert>
			{/if}
		</form>
	</div>
</Card>
