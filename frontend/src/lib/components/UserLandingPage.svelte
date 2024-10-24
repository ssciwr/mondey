<script lang="ts">
	import UserVerify from '$lib/components/UserVerify.svelte';
	import { componentTable } from '$lib/stores/componentStore';
	import { currentUser, refresh } from '$lib/stores/userStore';
	import { TabItem, Tabs } from 'flowbite-svelte';
	import { AtomOutline, CogSolid, GridPlusSolid, ProfileCardSolid } from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { get } from 'svelte/store';

	console.log('user: ', get(currentUser));

	onMount(async () => {
		await refresh();
	});

	const isVerifed = get(currentUser)?.is_verified;

	export let userData: any[];
</script>

{#if isVerifed === true}
	<div class="m-2 p-2">
		<Tabs tabStyle="pill">
			<TabItem open={true}>
				<div slot="title" class="flex items-center gap-2 text-lg">
					<ProfileCardSolid size="lg" />
					Persönliche Daten
				</div>
				<svelte:component this={componentTable['userDataInput']} data={userData} />
			</TabItem>
			<TabItem>
				<div slot="title" class="flex items-center gap-2 text-lg">
					<GridPlusSolid size="lg" />
					Kinder
				</div>
				<svelte:component this={componentTable['childrenGallery']} />
			</TabItem>

			{#if get(currentUser)?.is_superuser}
				<TabItem>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<CogSolid size="lg" />
						{$_('admin.title')}
					</div>
					<svelte:component this={componentTable['adminPage']} />
				</TabItem>
			{/if}
			{#if get(currentUser)?.is_researcher}
				<TabItem>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<AtomOutline size="lg" />
						{$_('researcher.title')}
					</div>
					<svelte:component this={componentTable['researchPage']} />
				</TabItem>
			{/if}
		</Tabs>
	</div>
{:else}
	<UserVerify />
{/if}
