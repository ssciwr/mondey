<script lang="ts">
import { afterNavigate, goto } from "$app/navigation";
import { base } from "$app/paths";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DarkModeChooser from "$lib/components/DarkModeChooser.svelte";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import UserVerify from "$lib/components/UserVerify.svelte";
import UserlandSidebar from "$lib/components/UserlandSidebar.svelte";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage, componentTable } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import { Button } from "flowbite-svelte";
import {
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
	BarsOutline,
	CogSolid,
	GridPlusSolid,
	LanguageOutline,
	ProfileCardSolid,
	SunOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

let showAlert: boolean = $state(false);
let alertMessage: string = $state(i18n.tr.login.alertMessageError);
let hideDrawer: boolean = $state(true);

// get user state
onMount(user.load);

// set this initially to user data such that the user data page is shown first
activePage.set("childrenGallery");

afterNavigate(() => {
	hideDrawer = true;
});
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
			<div class = "flex flex-row items-start text-sm md:text-base" >

				<!-- desktop version: only sidebar-->
				<div class = "max-md:hidden m-2 p-2 ">
					<UserlandSidebar setHideDrawer={(to) => { hideDrawer = to }} />
				</div>

				<!-- mobile version: drawer instead of fixed sidebar-->
				<button id="drawerButton" class="fixed right-6 top-7 bg-white text-gray-800 dark:bg-gray-800 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 p-1 rounded md:hidden"
				onclick={()=>{hideDrawer = !hideDrawer}}> <BarsOutline size="lg" /></button>

				<Drawer transitionType="fly" placement="right" transitionParams={{duration: 200}} bind:hidden = {hideDrawer} id="menuDrawer">
					<UserlandSidebar setHideDrawer={(to) => { hideDrawer = to }} />
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
