<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import logo_dark from "$lib/assets/mondey_dark.svg";
import logo_light from "$lib/assets/mondey_light.svg";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import Footer from "$lib/components/Navigation/Footer.svelte";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {Button, NavBrand, NavHamburger, NavUl, Navbar, NavLi, DarkMode} from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
import { onMount } from "svelte";

import "../app.css";
import FunctionalIcon from "$lib/components/Navigation/FunctionalIcon.svelte";
import DarkModeChooser from "$lib/components/DarkModeChooser.svelte";

import { page } from '$app/stores';
const isUserLand = $page.url.pathname.includes('/userLandingpage');
// Done this way because, other approaches to the layout (like a different +layout for userLand) would largely duplicate this one, but it is still hardcoded.

let { children } = $props();

onMount(async () => {
	await i18n.load();
	await user.load();
});
</script>

<svelte:head>
	<title>MONDEY :: Milestones of Normal Development in Early Years</title>
</svelte:head>

<Navbar>
	<NavBrand href={base}>
		<img src={logo_light} class="mt-6 block h-12 dark:hidden" alt="MONDEY Logo" />
		<img src={logo_dark} class="mt-6 hidden h-12 dark:block" alt="MONDEY Logo" />
	</NavBrand>
	{#if false === isUserLand}
		<NavHamburger />
		<NavUl ulClass="flex flex-col md:flex-row md:space-x-6 md:justify-right items-center">
			<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.latest}</NavLi>
			<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.downloads}</NavLi>
			<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.contact}</NavLi>

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

<div
	class="flex-auto items-center justify-center overflow-y-auto pb-2 mb-2"
>
	{@render children?.()}
</div>

<Footer/>
