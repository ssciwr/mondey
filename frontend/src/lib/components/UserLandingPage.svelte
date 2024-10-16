<script lang="ts">
	import { activeTabChildren, activeTabPersonal, componentTable } from '$lib/stores/componentStore';
	import { currentUser } from '$lib/stores/userStore';
	import { TabItem, Tabs } from 'flowbite-svelte';
	import { GridPlusSolid, ProfileCardSolid } from 'flowbite-svelte-icons';
	import { get } from 'svelte/store';
	import UserVerify from './UserVerify.svelte';

	import { onDestroy } from 'svelte';

	const isVerifed = get(currentUser)?.is_verified;
	let currentPersonal = 'userDataInput';
	let currentChildren = 'childrenGallery';
	export let userData: any[];

	const unsubscribePersonal = activeTabPersonal.subscribe((value) => {
		currentPersonal = value;
	});

	const unsubscribeChildren = activeTabChildren.subscribe((value) => {
		currentChildren = value;
	});

	onDestroy(() => {
		unsubscribeChildren();
		unsubscribePersonal();
	});
	console.log('user: ', get(currentUser));
	console.log('  verified: ', isVerifed);
</script>

{#if isVerifed === true}
	<div class="m-2 p-2">
		<Tabs tabStyle="pill">
			<TabItem open={true}>
				<div slot="title" class="flex items-center gap-2 text-lg">
					<ProfileCardSolid size="lg" />
					Persönliche Daten
				</div>
				<svelte:component this={componentTable[currentPersonal]} data={userData} />
			</TabItem>
			<TabItem>
				<div slot="title" class="flex items-center gap-2 text-lg">
					<GridPlusSolid size="lg" />
					Kinder
				</div>
				<svelte:component this={componentTable[currentChildren]} />
			</TabItem>
		</Tabs>
	</div>
{:else}
	<UserVerify />
{/if}
