<script lang="ts">
import UserVerify from "$lib/components/UserVerify.svelte";
import { i18n } from "$lib/i18n.svelte";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import { Button, Card, TabItem, Tabs } from "flowbite-svelte";
import {
	AdjustmentsVerticalOutline,
	AtomOutline,
	CogSolid,
	GridPlusSolid,
	ProfileCardSolid,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import AdminPage from "./AdminPage.svelte";
import UserDataInput from "./UserDataInput.svelte";
import UserSettings from "./UserSettings.svelte";

onMount(user.load);
</script>

{#if user.data}
	{#if user.data.is_verified === true}
		<div class="m-2 p-2">
			<Tabs tabStyle="underline">
				<TabItem open={true}>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<ProfileCardSolid size="lg" />
						<span class="hidden md:inline">{i18n.tr.userData.label}</span>
					</div>
					<UserDataInput />
				</TabItem>
				<TabItem onclick = {() =>{
					activeTabChildren.set("childrenGallery");
				}}>
					<div slot="title" class="flex items-center gap-2 text-lg">
						<GridPlusSolid size="lg" />
						<span class="hidden md:inline">{i18n.tr.childData.overviewLabel}</span>
					</div>
					<svelte:component
						this={componentTable[$activeTabChildren]}
					/>
				</TabItem>
				{#if user.data.is_superuser}
					<TabItem>
						<div
							slot="title"
							class="flex items-center gap-2 text-lg"
						>
							<CogSolid size="lg" />
							<span class="hidden md:inline">{i18n.tr.admin.label}</span>
						</div>
						<AdminPage />
					</TabItem>
				{/if}
				{#if user.data.is_researcher}
					<TabItem>
						<div
							slot="title"
							class="flex items-center gap-2 text-lg"
						>
							<AtomOutline size="lg" />
							<span class="hidden md:inline">{i18n.tr.researcher.label}</span>
						</div>
						<Card />
					</TabItem>
				{/if}
				<TabItem>
					<div
						slot="title"
						class="flex items-center gap-2 text-lg"
					>
						<AdjustmentsVerticalOutline size="lg" />
						<span class="hidden md:inline">{i18n.tr.userData.settings}</span>
					</div>
					<UserSettings />
				</TabItem>
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
			{i18n.tr.login.notLoggedIn}
		</div>
	</div>
	<Button
		type="button"
		class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
		href="/"
	>
		{i18n.tr.registration.goHome}
	</Button>
{/if}
