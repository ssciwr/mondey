<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import logo_dark from "$lib/assets/mondey_dark.svg";
import logo_light from "$lib/assets/mondey_light.svg";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import FunctionalIcon from "$lib/components/Navigation/FunctionalIcon.svelte";
import UserProfile from "$lib/components/UserProfile.svelte";
import "$lib/i18n";
import { getTranslations } from "$lib/i18n";
import { user } from "$lib/stores/userStore.svelte";
import {
	Avatar,
	DarkMode,
	NavBrand,
	NavHamburger,
	NavLi,
	NavUl,
	Navbar,
} from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

import "../app.css";

let { children } = $props();

onMount(async () => {
	await user.load();
	getTranslations();
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
		<NavLi class = "hover:cursor-pointer" href={base}>{$_("misc.latest")}</NavLi>
		<NavLi class = "hover:cursor-pointer" href={base}>{$_("misc.downloads")}</NavLi>
		<NavLi class = "hover:cursor-pointer" href={base}>{$_("misc.contact")}</NavLi>

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
