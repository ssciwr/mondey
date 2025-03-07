<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage, componentTable } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import { Button, Card, TabItem, Tabs } from "flowbite-svelte";
import {
	Sidebar,
	SidebarGroup,
	SidebarItem,
	SidebarWrapper,
} from "flowbite-svelte";
import {
	AdjustmentsVerticalOutline,
	ArrowRightToBracketOutline,
	AtomOutline,
	CogSolid,
	GridPlusSolid,
	ProfileCardSolid,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

let showAlert: boolean = $state(false);
let alertMessage: string = $state(i18n.tr.login.alertMessageError);

onMount(user.load);

$effect(() => {
	console.log("active page: ", $activePage);
});

// set this initially to user data such that the user data page is shown first
activePage.set("userDataInput");
</script>


{#if showAlert}
<AlertMessage
	title={i18n.tr.login.alertMessageTitle}
	message={alertMessage}
	onclick={() => {
		showAlert = false;
	}}
/>
{:else}
	{#if user.data}
		{#if user.data.is_verified === true}
			<div class = "flex flex-row items-start" >
				<Sidebar class= "m-2 p-2 ">
					<SidebarWrapper>
						<SidebarGroup>
							<SidebarItem label = {i18n.tr.userData.label} onclick = {() => {
								activePage.set("userDataInput");
							}}>
								<svelte:fragment slot="icon">
									<ProfileCardSolid size="lg" />
								</svelte:fragment>
							</SidebarItem>

							<SidebarItem label = {i18n.tr.childData.overviewLabel} onclick = {() => {
								activePage.set("childrenGallery");
							}}>
								<svelte:fragment slot="icon">
									<GridPlusSolid size="lg" />
								</svelte:fragment>
							</SidebarItem>

							{#if user.data.is_superuser}
								<SidebarItem label = {i18n.tr.admin.label} onclick = {() => {
									activePage.set("adminPage");
								}}>
									<svelte:fragment slot="icon">
										<CogSolid size="lg" />
									</svelte:fragment>
								</SidebarItem>
							{/if}

							{#if user.data.is_researcher}
								<SidebarItem label = {i18n.tr.researcher.label}  onclick = {() => {
									activePage.set("researchPage");
								}}>
									<svelte:fragment slot="icon">
										<AtomOutline size="lg" />
									</svelte:fragment>
								</SidebarItem>
							{/if}
						</SidebarGroup>
						<SidebarGroup border>
							<SidebarItem label = {i18n.tr.userData.settingsLabel} onclick = {
								() => {
									activePage.set("settings");
								}
							}>
								<svelte:fragment slot="icon">
									<AdjustmentsVerticalOutline size="lg" />
								</svelte:fragment>
							</SidebarItem>

							<SidebarItem label = {i18n.tr.login.profileButtonLabelLogout} onclick = {async () => {
								const response = await user.logout();
								if (response.error) {
									alertMessage = i18n.tr.login.alertMessageError;
									showAlert = true;
								} else {
									console.log("Logout successful");
									user.data = null;
									currentChild.id = null;
									currentChild.data = null;
									goto(`/${base}`);
								}

							}}>
								<svelte:fragment slot="icon">
									<ArrowRightToBracketOutline size="lg" />
								</svelte:fragment>
							</SidebarItem>
						</SidebarGroup>
					</SidebarWrapper>
				</Sidebar >

				<svelte:component this={componentTable[$activePage]} class = "m-2 p-2"/>
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
{/if}
