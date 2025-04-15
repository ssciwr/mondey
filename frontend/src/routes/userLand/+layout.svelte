<script lang="ts">
import { afterNavigate, goto } from "$app/navigation";
import { page } from "$app/state";
import UserVerify from "$lib/components/UserVerify.svelte";
import UserlandSidebar from "$lib/components/UserlandSidebar.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Button } from "flowbite-svelte";
import { Drawer } from "flowbite-svelte";
import { BarsOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let hideDrawer: boolean = $state(true);

// get user state
onMount(async () => {
	await user.load();
	if (!user.data) {
		goto(`/login?intendedpath=${page.url.pathname}`);
	}
});

afterNavigate(() => {
	hideDrawer = true;
});

let { children } = $props();
</script>


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

                <div class = "m-2 p-2 w-full pl-2 md:pl-12 md:w-auto grow">
                    {@render children?.()}
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

{#if user.isTestAccount}
    <div class="fixed bottom-0 left-0 right-0 m-4 rounded-xl bg-white dark:bg-gray-700 border-solid border-2 shadow-xl p-8 border-gray-400 dark:border-gray-600 dark:text-white">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <h2 class="text-lg mb-4 md:mb-0">
                <strong>{i18n.tr.login.demoAccountNotification}</strong>
            </h2>
            <div class="flex justify-center md:justify-end">
                <Button on:click={() => goto("/signup")} class="text-bold text-md  w-full bg-primary-700 text-white dark:bg-white dark:text-gray-700  hover:opacity-80  hover:text-white">{i18n.tr.frontpage.buttonLabel}</Button>
            </div>
        </div>
    </div>
{/if}
