<script lang="ts">
import UserVerify from "$lib/components/UserVerify.svelte";
import { componentTable } from "$lib/stores/componentStore";
import { currentUser, refreshUser } from "$lib/stores/userStore";
import { Button, TabItem, Tabs } from "flowbite-svelte";
import {
	AtomOutline,
	CogSolid,
	GridPlusSolid,
	ProfileCardSolid,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";
import { get } from "svelte/store";

console.log("user: ", get(currentUser));

onMount(async () => {
	await refreshUser();
});
</script>

{#if get(currentUser)}
	{#if get(currentUser)?.is_verified === true}
		<div class="m-2 p-2">
			<Tabs tabStyle="pill">
				<TabItem open={true}>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<ProfileCardSolid size="lg" />
						Persönliche Daten
					</div>
					<svelte:component this={componentTable['userDataInput']} />
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
							{$_('admin.heading')}
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
{:else}
	<div
		class="m-2 mx-auto flex w-full items-center justify-center p-2 text-gray-700 dark:text-gray-400"
	>
		<div class="m-2 p-2">
			{$_('login.notLoggedIn')}
		</div>
	</div>
	<Button
		type="button"
		class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
		href="/"
	>
		{$_('registration.goHome')}
	</Button>
{/if}
