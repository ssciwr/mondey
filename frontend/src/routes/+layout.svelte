<svelte:options runes={true} />
<script lang="ts">
import { resolve } from "$app/paths";
import logo_dark from "#lib/assets/mondey_dark.svg";
import logo_dark_mobile from "#lib/assets/mondey_dark_mobile.svg";
import logo_light from "#lib/assets/mondey_light.svg";
import logo_light_mobile from "#lib/assets/mondey_light_mobile.svg";
import { installSessionExpiryHandler } from "#lib/auth/sessionExpiry.ts";
import { buttonClasses } from "#lib/buttonClasses.ts";
import DarkModeChooser from "#lib/components/DarkModeChooser.svelte";
import LocaleChooser from "#lib/components/LocaleChooser.svelte";
import Footer from "#lib/components/Navigation/Footer.svelte";
import SessionReauthenticationModal from "#lib/components/SessionReauthenticationModal.svelte";
import { i18n } from "#lib/i18n.svelte.ts";
import { alertStore } from "#lib/stores/alertStore.svelte.ts";
import { user } from "#lib/stores/userStore.svelte.ts";
import { translationIds } from "#lib/translations.ts";

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
	ThemeProvider,
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
import LocaleSidebarDropdown from "#lib/components/LocaleSidebarDropdown.svelte";
import { flowbiteTheme } from "#lib/flowbiteTheme.ts";

/* So basically it's not ideal to detect user being in the userland this way, but the main menu for non-logged in users
does make sense to be here.

Best would be to refactor to have a static non-logged in part (e.g. "/") and have this user part just for logged in
users with only the logged in stuff, so no intermixing in files like this. However, that refactor isn't worth the
time/risk necessarily.
 */
let isUserLand = $derived(page.url.pathname.includes("userLand/"));
afterNavigate(() => {
	drawerOpen = false;
});
// Done this way because, other approaches to the layout (like a different +layout for userLand) would largely duplicate this one, but it is still hardcoded.

let { children } = $props();
let drawerOpen = $state(false);

onMount(() => {
	const uninstallSessionExpiryHandler = installSessionExpiryHandler();
	void (async () => {
		await user.load();
		await i18n.load();
	})();
	return uninstallSessionExpiryHandler;
});
function toggleDrawer() {
	drawerOpen = !drawerOpen;
}

const alertModalColorClasses: Record<"red" | "yellow", string> = {
	red: "bg-red-50 text-red-800 border-red-300 divide-red-300 dark:text-red-400 dark:border-red-800 dark:divide-red-800",
	yellow:
		"bg-yellow-50 text-yellow-800 border-yellow-300 divide-yellow-300 dark:text-yellow-300 dark:border-yellow-800 dark:divide-yellow-800",
};
// white icon buttons in the mobile header
const mobileIconButtonClass = `${buttonClasses.primary} ${buttonClasses.icon} rounded-md p-2 bg-white text-primary-700 hover:bg-white dark:bg-primary-700 dark:text-white dark:hover:bg-primary-700`;

let alertModalColor: "red" | "yellow" | undefined = $derived(
	alertStore.isError ? "red" : alertStore.isAwaitError ? "yellow" : undefined,
);
</script>

<svelte:head>
	<title>MONDEY :: Milestones of Normal Development in Early Years</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
	<!-- For iPhone 12 Chrome view width issues -->
</svelte:head>

<ThemeProvider theme={flowbiteTheme}>

	<div class="fixed inset-x-0 pt-[1.1rem] pb-4 border-b border-[lightgray] bg-white z-1000 dark:bg-gray-800 md:hidden w-full text-center flex justify-center items-center shadow-lg">
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
				<NavUl classes={{ ul: "flex flex-col p-0 md:flex-row md:gap-6 md:justify-right md:text-[1rem] md:font-normal items-center" }}>
					<NavLi class="hover:cursor-pointer md:p-0" href="/aktuelles">{i18n.tr.misc.latest}</NavLi>
					<NavLi class="hover:cursor-pointer md:p-0" href="/downloads">{i18n.tr.misc.downloads}</NavLi>
					<NavLi class="hover:cursor-pointer md:p-0" href="/static/kontakt">{i18n.tr.misc.contact}</NavLi>

					<DarkModeChooser />
					{#if user.data === null}
						<Button
								type="button"
								class="my-2 w-full"
								href={resolve("/login")}
								size="lg">{i18n.tr.login.profileButtonLabelDefault}</Button
						>
					{:else}
						<Button
								type="button"
								class="my-2 w-full"
								href={resolve("/userLand/children")}
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
		<div class="min-h-20"></div>

		{#if false === isUserLand}
			<!-- Mobile Log in -->
			<div class="z-1000 fixed top-[0.8rem] left-4">
				<Button class={mobileIconButtonClass} href="/login">
					<UserOutline />
				</Button>
			</div>
			<!-- Mobile Navigation -->
			<div class="z-1000 fixed top-[0.8rem] right-4">
				<Button
					class={mobileIconButtonClass}
					onclick={toggleDrawer}
					aria-label={i18n.tr.misc.menu ?? translationIds.misc.menu}
					aria-expanded={drawerOpen}
					aria-controls="sidebar"
				>
					<BarsOutline />
				</Button>
			</div>

			<!-- Mobile Drawer -->
			<Drawer placement="right" bind:open={drawerOpen} id="sidebar">
				<!-- receives the initial focus, otherwise the first button in the drawer is focused and shows its tooltip -->
				<span data-autofocus tabindex="-1" class="absolute outline-hidden"></span>
				<Sidebar disableBreakpoints position="static">
						<SidebarGroup class="space-y-2 mt-10">
							<!-- Navigation Items -->
							<SidebarItem label={i18n.tr.misc.latest} href="/aktuelles">
								{#snippet icon()}
									<BarsOutline size="lg" />
								{/snippet}
							</SidebarItem>
							<SidebarItem label={i18n.tr.misc.downloads} href="/downloads">
								{#snippet icon()}
									<BarsOutline size="lg" />
								{/snippet}
							</SidebarItem>
							<SidebarItem label={i18n.tr.misc.contact} href="/static/kontakt">
								{#snippet icon()}
									<BarsOutline size="lg" />
								{/snippet}
							</SidebarItem>

							{#if user.data === null}
								<SidebarItem label={i18n.tr.login.profileButtonLabelDefault}
											 href="/login">
									{#snippet icon()}
										<ProfileCardSolid size="lg" />
									{/snippet}
								</SidebarItem>
							{:else}
								<SidebarItem label={i18n.tr.registration.goHome}
											 href="/userLand/children">
									{#snippet icon()}
										<ProfileCardSolid size="lg" />
									{/snippet}
								</SidebarItem>
							{/if}
						</SidebarGroup>
						<SidebarGroup border borderClass="space-y-2 pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
							<!-- Settings -->
							<SidebarItem>
								{#snippet icon()}
									<SunOutline />
								{/snippet}
								{#snippet subtext()}
									<DarkModeChooser />
								{/snippet}
							</SidebarItem>
							<LocaleSidebarDropdown />
						</SidebarGroup>
				</Sidebar>
			</Drawer>
		{/if}
	</div>

	<div
			class="flex-auto items-center justify-center overflow-y-auto pb-2 mb-2 main-content"
	>
		{@render children?.()}
	</div>

	<Modal
		data-testid="alert-modal"
		bind:open={alertStore.isAlertShown}
		class={alertModalColor ? alertModalColorClasses[alertModalColor] : undefined}
		classes={alertModalColor ? { header: `text-gray-900 dark:text-white ${alertModalColorClasses[alertModalColor]}` } : undefined}
		title={alertStore.title}
		autoclose>
		<p class="text-base">{alertStore.message}</p>
		{#snippet footer()}
			<Button class={`${buttonClasses.primary} ${buttonClasses.large}`} onclick={() => {
				if (alertStore.callback) {
					alertStore.callback();
				}
				alertStore.hideAlert();
			}}>{alertStore.buttonText ?? i18n.tr.misc.understood}</Button>
		{/snippet}
	</Modal>

	<SessionReauthenticationModal />


	<Footer/>
</ThemeProvider>
