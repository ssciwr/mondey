<script lang="ts">
import { afterNavigate, goto } from "$app/navigation";
import UserVerify from "$lib/components/UserVerify.svelte";
import UserlandSidebar from "$lib/components/UserlandSidebar.svelte";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Button, Drawer } from "flowbite-svelte";
import { BarsOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let drawerOpen: boolean = $state(false);

// get user state
onMount(user.load);

afterNavigate(() => {
	drawerOpen = false;
});
</script>


	{#if user.data}
		{#if user.data.is_verified === true}
			<div class = "flex flex-row items-start text-sm md:text-base" >

				<!-- desktop version: only sidebar-->
				<div class = "max-md:hidden m-2 p-2 ">
					<UserlandSidebar setHideDrawer={(to) => { drawerOpen = !to }} />
				</div>

				<!-- mobile version: drawer instead of fixed sidebar-->
				<button id="drawerButton" class="z-1001 fixed right-6 top-7 bg-white text-gray-800 dark:bg-gray-800 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 p-1 rounded-sm md:hidden"
				onclick={()=>{drawerOpen = !drawerOpen}}> <BarsOutline size="lg" /></button>

				<Drawer placement="right" transitionParams={{duration: 200}} bind:open={drawerOpen} id="menuDrawer">
					<!-- receives the initial focus, otherwise the first button in the drawer is focused and shows its tooltip -->
					<span data-autofocus tabindex="-1" class="absolute outline-hidden"></span>
					<UserlandSidebar setHideDrawer={(to) => { drawerOpen = !to }} />
				</Drawer>
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
