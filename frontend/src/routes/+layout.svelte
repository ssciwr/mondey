<script lang="ts">
	import '$lib/i18n';
	import logo_dark from '$lib/assets/mondey_dark.svg';
	import logo_light from '$lib/assets/mondey_light.svg';
	import FunctionalIcon from '$lib/components/Navigation/FunctionalIcon.svelte';
	import UserProfile from '$lib/components/UserProfile.svelte';
	import LocaleChooser from '$lib/components/LocaleChooser.svelte';
	import { Avatar, DarkMode, Navbar, NavBrand, NavHamburger, NavLi, NavUl } from 'flowbite-svelte';
	import { MoonSolid, SunSolid } from 'flowbite-svelte-icons';
	import '../app.css';
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { getTranslations } from '$lib/i18n';

	onMount(() => {
		getTranslations();
	});
</script>

<Navbar>
	<NavBrand href={base}>
		<img src={logo_light} class="mt-6 block h-12 dark:hidden" alt="MONDEY Logo" />
		<img src={logo_dark} class="mt-6 hidden h-12 dark:block" alt="MONDEY Logo" />
	</NavBrand>
	<NavHamburger />
	<NavUl ulClass="hidden flex min-[320px]:flex-col sm:flex-col md:flex-row items-center lg:mt-8 lg:space-x-14 md:mt-8 md:space-x-7 text-lg ">
		<NavLi href={base}>Aktuelles</NavLi>
		<NavLi href={base}>Downloads</NavLi>
		<NavLi href={base}>Kontakt</NavLi>

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
	<slot></slot>
</div>
