<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import logo_dark from "$lib/assets/mondey_dark.svg";
import logo_dark_mobile from "$lib/assets/mondey_dark_mobile.svg";
import logo_light from "$lib/assets/mondey_light.svg";
import logo_light_mobile from "$lib/assets/mondey_light_mobile.svg";
import DarkModeChooser from "$lib/components/DarkModeChooser.svelte";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import Footer from "$lib/components/Navigation/Footer.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";

import {
	Button,
	Drawer,
	Modal,
	NavBrand,
	NavHamburger,
	NavLi,
	NavUl,
	Navbar,
	Sidebar,
	SidebarGroup,
	SidebarItem,
	SidebarWrapper,
} from "flowbite-svelte";
import {
	BarsOutline,
	LanguageOutline,
	ProfileCardSolid,
	SunOutline,
	UserOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

import "../app.css";

import { afterNavigate } from "$app/navigation";
import { page } from "$app/state";
import LocaleSidebarDropdown from "$lib/components/LocaleSidebarDropdown.svelte";

/* So basically it's not ideal to detect user being in the userland this way, but the main menu for non-logged in users
does make sense to be here.

Best would be to refactor to have a static non-logged in part (e.g. "/") and have this user part just for logged in
users with only the logged in stuff, so no intermixing in files like this. However, that refactor isn't worth the
time/risk necessarily.
 */
let isUserLand = $derived(page.url.pathname.includes("userLand/"));
afterNavigate(() => {
	hideDrawer = true;
});
// Done this way because, other approaches to the layout (like a different +layout for userLand) would largely duplicate this one, but it is still hardcoded.

let { children } = $props();
let hideDrawer = $state(true);

onMount(async () => {
	await user.load();
	await i18n.load();
});
function toggleDrawer() {
	hideDrawer = !hideDrawer;
}
</script>

<svelte:head>
	<title>MONDEY :: Milestones of Normal Development in Early Years</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
	<!-- For iPhone 12 Chrome view width issues -->
</svelte:head>

<div style="position:fixed;padding-top:1.1rem;padding-bottom:1rem;left:0px;right:0px;border-bottom:1px solid lightgray"
	 class="bg-white z-1000 dark:bg-gray-800 md:hidden w-full text-center flex justify-center items-center shadow-lg">
	<a href="/#">
		<!-- Desktop logos -->
		<img src={logo_light} class="hidden sm:block dark:hidden h-10" alt="MONDEY Logo" />
		<img src={logo_dark} class="hidden sm:dark:block h-10" alt="MONDEY Logo" />
		<!-- Mobile logos -->
		<img src={logo_light_mobile} class="block sm:hidden dark:hidden h-10" alt="MONDEY Logo" />
		<img src={logo_dark_mobile} class="hidden dark:block sm:dark:hidden h-10" alt="MONDEY Logo" />
	</a>
</div>
<!-- Desktop Navigation -->
<div class="hidden md:block">
	<Navbar>
		<div>
			<NavBrand href="/#" class="z-1000">
				<img src={logo_light} class="mt-6 block h-12 dark:hidden" alt="MONDEY Logo" />
				<img src={logo_dark} class="mt-6 hidden h-12 dark:block" alt="MONDEY Logo" />
			</NavBrand>
		</div>
		{#if false === isUserLand}
			<NavHamburger />
			<NavUl ulClass="flex flex-col md:flex-row md:space-x-6 md:justify-right items-center">
				<NavLi class="hover:cursor-pointer" href="/aktuelles">{i18n.tr.misc.latest}</NavLi>
				<NavLi class="hover:cursor-pointer" href="/static/downloads">{i18n.tr.misc.downloads}</NavLi>
				<NavLi class="hover:cursor-pointer" href="/static/kontakt">{i18n.tr.misc.contact}</NavLi>

				<DarkModeChooser />
				{#if user.data === null}
					<Button
							type="button"
							class="m-2 w-full"
							href="{base}/login"
							size="lg">{i18n.tr.login.profileButtonLabelDefault}</Button
					>
				{:else}
					<Button
							type="button"
							class="m-2 w-full"
							href="{base}/userLand/children"
							size="lg">{i18n.tr.registration.goHome}</Button
					>
				{/if}

				<LocaleChooser withIcon={true}/>
			</NavUl>
		{/if}
	</Navbar>
</div>

<!-- Mobile Layout -->
<div class="md:hidden">
	<!-- Spacer to account for fixed header -->
	<div style="min-height:5rem"></div>

	{#if false === isUserLand}
		<!-- Mobile Log in -->
		<div class="z-1000 fixed" style="top:0.8rem;left:1rem;">
			<a class="btn-primary btn-icon" href="/login">
				<UserOutline />
			</a>
		</div>
		<!-- Mobile Navigation -->
		<div class="z-1000 fixed" style="top:0.8rem;right:1rem;">
			<div class="btn-primary btn-icon" onclick={toggleDrawer} >
				<BarsOutline class="cursor-pointer" />
			</div>
		</div>

		<!-- Mobile Drawer -->
		<Drawer placement="right" bind:hidden={hideDrawer} id="sidebar">
			<Sidebar>
				<SidebarWrapper>
					<SidebarGroup class="mt-10">
						<!-- Navigation Items -->
						<SidebarItem label={i18n.tr.misc.latest} href="/aktuelles">
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>
						<SidebarItem label={i18n.tr.misc.downloads} href="/static/downloads">
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>
						<SidebarItem label={i18n.tr.misc.contact} href="/static/kontakt">
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>

						{#if user.data === null}
							<SidebarItem label={i18n.tr.login.profileButtonLabelDefault}
										 href="/login">
								<svelte:fragment slot="icon">
									<ProfileCardSolid size="lg" />
								</svelte:fragment>
							</SidebarItem>
						{:else}
							<SidebarItem label={i18n.tr.registration.goHome}
										 href="/userLand/children">
								<svelte:fragment slot="icon">
									<ProfileCardSolid size="lg" />
								</svelte:fragment>
							</SidebarItem>
						{/if}
					</SidebarGroup>
					<SidebarGroup border>
						<!-- Settings -->
						<SidebarItem>
							<svelte:fragment slot="icon">
								<SunOutline />
							</svelte:fragment>
							<svelte:fragment slot="subtext">
								<DarkModeChooser />
							</svelte:fragment>
						</SidebarItem>
						<LocaleSidebarDropdown />
					</SidebarGroup>
				</SidebarWrapper>
			</Sidebar>
		</Drawer>
	{/if}
</div>

<div
		class="flex-auto items-center justify-center overflow-y-auto pb-2 mb-2 main-content"
>
	{@render children?.()}
</div>

<Modal data-testid="alert-modal" bind:open={alertStore.isAlertShown} color={alertStore.isError ? 'red' : alertStore.isAwaitError ? 'yellow' : 'default'} title={alertStore.title} autoclose>
	<p class="text-base">{alertStore.message}</p>
	<svelte:fragment slot="footer">
		<button class="btn-primary" onclick={() => {
			if (alertStore.callback) {
				alertStore.callback();
			}
			alertStore.hideAlert();
		}}>{i18n.tr.misc.understood}</button>
	</svelte:fragment>
</Modal>


<Footer/>
