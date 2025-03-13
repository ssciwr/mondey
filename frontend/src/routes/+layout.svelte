<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import logo_dark from "$lib/assets/mondey_dark.svg";
import logo_light from "$lib/assets/mondey_light.svg";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import Footer from "$lib/components/Navigation/Footer.svelte";
import FunctionalIcon from "$lib/components/Navigation/FunctionalIcon.svelte";
import UserProfile from "$lib/components/UserProfile.svelte";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Avatar,
	DarkMode,
	NavBrand,
	NavHamburger,
	NavLi,
	NavUl,
	Navbar, Button,
} from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
import { onMount } from "svelte";

import "../app.css";

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
	<NavHamburger />
	<NavUl ulClass="hidden flex min-[320px]:flex-col sm:flex-col md:flex-row items-center lg:mt-8 lg:space-x-14 md:mt-8 md:space-x-7 text-lg ">
		<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.latest}</NavLi>
		<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.downloads}</NavLi>
		<NavLi class = "hover:cursor-pointer" href={base}>{i18n.tr.misc.contact}</NavLi>

		<FunctionalIcon tooltip={'Darkmode ein- oder ausschalten'}>
			<DarkMode class="apply-icon-style">
				<MoonSolid slot="darkIcon" />
				<SunSolid slot="lightIcon" />
			</DarkMode>
		</FunctionalIcon>

		<FunctionalIcon>
			<Avatar rounded class="apply-icon-style" id="avatar" />
		</FunctionalIcon>

		<UserProfile triggeredBy="#avatar" />

		<LocaleChooser />
	</NavUl>
</Navbar>

<div
	class="flex-auto  items-center justify-center overflow-y-auto pb-20 md:mx-[max(10vw,2rem)] md:my-[max(2vw,2rem)]"
>
	{@render children?.()}
</div>

<div class="fixed bottom-0 left-0 right-0 m-4 rounded-xl bg-white dark:bg-gray-700 border-solid border-4 p-8 border-gray-400 dark:border-gray-600 dark:text-white">
	<div class="flex flex-col md:flex-row md:items-center md:justify-between">
		<h2 class="text-lg mb-4 md:mb-0">
			<strong>{i18n.tr.login.demoAccountNotification}</strong>
		</h2>
		<div class="flex justify-center md:justify-end">
			<Button class="text-bold text-md  w-full bg-primary-700 text-white dark:bg-white dark:text-gray-700  hover:opacity-80  hover:text-white">{i18n.tr.frontpage.buttonLabel}</Button>
		</div>
	</div>
</div>

<Footer/>
