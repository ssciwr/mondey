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
	Button,
	Heading,
	NavBrand,
	NavHamburger,
	NavUl,
	Navbar,
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

		{#if user.id !== null}
			<FunctionalIcon>
				<Avatar rounded class="apply-icon-style" id="avatar" />
			</FunctionalIcon>

			<UserProfile triggeredBy="#avatar" />
		{:else}
			<div
				class="mx-auto mb-6 flex flex-col items-center justify-center space-y-6"
			>
				<Heading tag="h3" class="mx-auto flex w-full justify-center"
					>{i18n.tr.login.profileTitleDefault}</Heading
				>
				<Button
					type="button"
					class="m-2 w-full"
					href="{base}/userLand/userLogin"
					size="lg">{i18n.tr.login.profileButtonLabelDefault}</Button
				>
			</div>
		{/if}
		<LocaleChooser />
	</NavUl>
</Navbar>

<div
	class="flex-auto items-center justify-center overflow-y-auto pb-20 md:mx-[max(10vw,2rem)] md:my-[max(2vw,2rem)]"
>
	{@render children?.()}
</div>

<Footer/>
