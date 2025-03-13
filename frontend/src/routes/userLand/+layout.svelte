<svelte:options runes={true} />
<script>
import {user} from "$lib/stores/userStore.svelte";
import {i18n} from "$lib/i18n.svelte";
import {goto} from "$app/navigation";
import {Button} from "flowbite-svelte";


let { children } = $props();
</script>

{@render children?.()}

{#if user.isTestAccount}
    <div class="fixed bottom-0 left-0 right-0 m-4 rounded-xl bg-white dark:bg-gray-700 border-solid border-1 p-8 border-gray-300 dark:border-gray-600 dark:text-white">
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