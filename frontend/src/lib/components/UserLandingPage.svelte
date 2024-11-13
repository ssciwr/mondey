<script lang="ts">
import UserVerify from "$lib/components/UserVerify.svelte";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { currentUser, refreshUser } from "$lib/stores/userStore";
import { Button, Card, TabItem, Tabs } from "flowbite-svelte";
import {
	AtomOutline,
	CogSolid,
	GridPlusSolid,
	ProfileCardSolid,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";
import { get } from "svelte/store";
import AdminPage from "./AdminPage.svelte";
import UserDataInput from "./UserDataInput.svelte";

onMount(async () => {
	await refreshUser();
});

let windowWidth = $state(1920);
let smallScreen = $derived(windowWidth < 800);
</script>
<svelte:window bind:innerWidth={windowWidth} />

{#if get(currentUser)}
	{#if get(currentUser)?.is_verified === true}
		<div class="m-2 p-2">
			<Tabs tabStyle="underline">
				<TabItem open={true}>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<ProfileCardSolid size="lg" />
						{#if smallScreen === false}
							{$_("userData.label")}
						{/if}
					</div>
					<svelte:component this={UserDataInput} />
				</TabItem>
				<TabItem onclick = {() =>{
					activeTabChildren.set("childrenGallery");
				}}>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<GridPlusSolid size="lg" />
						{#if smallScreen === false}
							{$_("childData.overviewLabel")}
						{/if}
					</div>
					<svelte:component
						this={componentTable[$activeTabChildren]}
					/>
				</TabItem>

				{#if get(currentUser)?.is_superuser}
					<TabItem>
						<div
							slot="title"
							class="flex items-center gap-2 text-lg"
						>
							<CogSolid size="lg" />
							{#if smallScreen === false}
								{$_("admin.label")}
							{/if}
						</div>
						<AdminPage />
					</TabItem>
				{/if}
				{#if get(currentUser)?.is_researcher}
					<TabItem>
						<div
							slot="title"
							class="flex items-center gap-2 text-lg"
						>
							<AtomOutline size="lg" />
							{#if smallScreen === false}
								{$_("researcher.label")}
							{/if}
						</div>
						<svelte:component this={Card} />
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
			{$_("login.notLoggedIn")}
		</div>
	</div>
	<Button
		type="button"
		class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
		href="/"
	>
		{$_("registration.goHome")}
	</Button>
{/if}
