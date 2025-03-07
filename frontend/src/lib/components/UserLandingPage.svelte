<script lang="ts">
import { goto } from "$app/navigation";
import { base } from "$app/paths";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage, componentTable } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import { hideDomain } from "@unovis/ts/components/axis/style";
import { Button } from "flowbite-svelte";
import {
	CloseButton,
	Drawer,
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
let hideDrawer: boolean = $state(true);

// get user state
onMount(user.load);

// set this initially to user data such that the user data page is shown first
activePage.set("userDataInput");
</script>

<!-- navigation menu definition-->
{#snippet sidebarNav()}
	<Sidebar>
		<SidebarWrapper>
			<SidebarGroup>
				<SidebarItem label = {user.data.email} class = "font-bold"/>
				<SidebarItem label = {i18n.tr.userData.label} onclick = {() => {
					activePage.set("userDataInput");
					hideDrawer = true;
				}}>
					<svelte:fragment slot="icon">
						<ProfileCardSolid size="lg" />
					</svelte:fragment>
				</SidebarItem>

				<SidebarItem label = {i18n.tr.childData.overviewLabel} onclick = {() => {
					activePage.set("childrenGallery");
					hideDrawer = true;
				}}>
					<svelte:fragment slot="icon">
						<GridPlusSolid size="lg" />
					</svelte:fragment>
				</SidebarItem>

				{#if user.data.is_superuser}
					<SidebarItem label = {i18n.tr.admin.label} onclick = {() => {
						activePage.set("adminPage");
						hideDrawer = true;
					}}>
						<svelte:fragment slot="icon">
							<CogSolid size="lg" />
						</svelte:fragment>
					</SidebarItem>
				{/if}

				{#if user.data.is_researcher}
					<SidebarItem label = {i18n.tr.researcher.label}  onclick = {() => {
						activePage.set("researchPage");
						hideDrawer = true;
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
						hideDrawer = true;
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
						hideDrawer = true;
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
{/snippet}


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
			<div class = "flex flex-row items-start text-sm md:text-base" >

				<!-- desktop version: only sidebar-->
				<div class = "max-md:hidden m-2 p-2 ">
					{@render sidebarNav()}
				</div>

				<!-- mobile version: drawer instead of fixed sidebar-->
				<Button size = "xl" id="drawerButton" class="fixed left-0 top-1/2 -translate-y-1/2  h-24 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600 p-2 rounded-r-lg md:hidden shadow-lg"
				onclick={()=>{hideDrawer = !hideDrawer}}><ArrowRightToBracketOutline  size="lg"/></Button>

				<Drawer transitionType="fly" transitionParams={{duration: 200}} bind:hidden = {hideDrawer} id="menuDrawer">
					{@render sidebarNav()}
				</Drawer>

				<div class = "m-2 p-2 w-full pl-12 md:pl-2 md:w-auto">
					<svelte:component this={componentTable[$activePage]}/>
				</div>
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
