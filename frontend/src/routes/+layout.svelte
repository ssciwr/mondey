<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import logo_dark from "$lib/assets/mondey_dark.svg";
import logo_light from "$lib/assets/mondey_light.svg";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import Footer from "$lib/components/Navigation/Footer.svelte";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Button,
	NavBrand,
	NavHamburger,
	NavLi,
	NavUl,
	Navbar, Drawer, SidebarWrapper, SidebarItem, Sidebar, SidebarGroup,
} from "flowbite-svelte";
import {
	BarsOutline,
	LanguageOutline,
	ProfileCardSolid,
	SunOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import { alertStoreSvelte } from "$lib/stores/alertStore.svelte";

import "../app.css";
import DarkModeChooser from "$lib/components/DarkModeChooser.svelte";

import { page } from "$app/stores";
import {isMobile} from "$lib/util";
let isUserLand = $derived($page.url.pathname.includes("userLandingpage"));
// Done this way because, other approaches to the layout (like a different +layout for userLand) would largely duplicate this one, but it is still hardcoded.

let { children } = $props();
let hideDrawer = $state(true);
let isMobilePhone = $state(false);

onMount(async () => {
	await i18n.load();
	await user.load();
	isMobilePhone = isMobile();
});
function toggleDrawer() {
	hideDrawer = !hideDrawer;
}
</script>

<svelte:head>
	<title>MONDEY :: Milestones of Normal Development in Early Years</title>
</svelte:head>

<div style="position:fixed;padding-top:1rem;padding-bottom:1rem;left:0px;right:0px"
	 class="bg-white dark:bg-gray-800 md:hidden w-full text-center flex justify-center items-center">
	<img src={logo_light} class="block h-14 dark:hidden" alt="MONDEY Logo" />
	<img src={logo_dark} class="hidden h-14 dark:block" alt="MONDEY Logo" />
</div>
<!-- Desktop Navigation -->
{#if false === isMobilePhone}
	<Navbar>
		<div class="hidden md:block">
			<NavBrand href={base}>
				<img src={logo_light} class="mt-6 block h-12 dark:hidden" alt="MONDEY Logo" />
				<img src={logo_dark} class="mt-6 hidden h-12 dark:block" alt="MONDEY Logo" />
			</NavBrand>
		</div>
		{#if false === isUserLand}
			<NavHamburger />
			<NavUl ulClass="flex flex-col md:flex-row md:space-x-6 md:justify-right items-center">
				<NavLi class="hover:cursor-pointer" href={base}>{i18n.tr.misc.latest}</NavLi>
				<NavLi class="hover:cursor-pointer" href={base}>{i18n.tr.misc.downloads}</NavLi>
				<NavLi class="hover:cursor-pointer" href={base}>{i18n.tr.misc.contact}</NavLi>

				<DarkModeChooser />
				{#if user.data === null}
					<Button
							type="button"
							class="m-2 w-full"
							href="{base}/userLand/userLogin"
							size="lg">{i18n.tr.login.profileButtonLabelDefault}</Button
					>
				{:else}
					<Button
							type="button"
							class="m-2 w-full"
							href="{base}/userLand/userLandingpage"
							size="lg">{i18n.tr.registration.goHome}</Button
					>
				{/if}

				<LocaleChooser withIcon={true}/>
			</NavUl>
		{/if}
	</Navbar>
{:else}
	<!-- Mobile Navigation -->

		<div class="z-10 fixed" style="top:1.8rem;right:1.5rem;">
			<BarsOutline size="xl" class="cursor-pointer" onclick={toggleDrawer} />
		</div>
	<div style="min-height:5rem"></div>

	<!-- Mobile Drawer -->
	<Drawer placement="right" bind:hidden={hideDrawer} id="sidebar">
			<Sidebar>
				<SidebarWrapper>
					<SidebarGroup>
						<!-- Navigation Items -->
						<SidebarItem label={i18n.tr.misc.latest} href={base}>
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>
						<SidebarItem label={i18n.tr.misc.downloads} href={base}>
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>
						<SidebarItem label={i18n.tr.misc.contact} href={base}>
							<svelte:fragment slot="icon">
								<BarsOutline size="lg" />
							</svelte:fragment>
						</SidebarItem>

						<!-- User Profile/Login -->
						{#if user.data === null}
							<SidebarItem label={i18n.tr.login.profileButtonLabelDefault} href="{base}/userLand/userLogin">
								<svelte:fragment slot="icon">
									<ProfileCardSolid size="lg" />
								</svelte:fragment>
							</SidebarItem>
						{:else}
							<SidebarItem label={i18n.tr.registration.goHome} href="{base}/userLand/userLandingpage">
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

						<SidebarItem>
							<svelte:fragment slot="icon">
								<LanguageOutline size="lg" />
							</svelte:fragment>
							<svelte:fragment slot="subtext">
								<LocaleChooser />
							</svelte:fragment>
						</SidebarItem>
					</SidebarGroup>
				</SidebarWrapper>
			</Sidebar>
	</Drawer>
{/if}

<div
	class="flex-auto items-center justify-center overflow-y-auto pb-2 mb-2"
>
	{@render children?.()}
</div>

{#if alertStoreSvelte.isAlertShown}
	<AlertMessage
			id="alertMessageSettings"
			title={alertStoreSvelte.title}
			message={alertStoreSvelte.message}
			isError={alertStoreSvelte.isError}
			onclick={() => {
				console.log('Callback clicked.')
			 if (alertStoreSvelte.callback) {
                alertStoreSvelte.callback();
             }
             alertStoreSvelte.hideAlert();

          }}
	/>
{/if}


<Footer/>
