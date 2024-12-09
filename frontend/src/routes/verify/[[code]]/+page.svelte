<script lang="ts">
import { page } from "$app/stores";
import { verifyVerify } from "$lib/client/services.gen";
import UserLogin from "$lib/components/UserLogin.svelte";
import {
	CheckCircleOutline,
	ExclamationCircleOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

onMount(async () => {
	const { data, error } = await verifyVerify({
		body: { token: $page.params.code },
	});
	if ((!error && data) || error?.detail === "VERIFY_USER_ALREADY_VERIFIED") {
		success = true;
		return;
	}
	console.log(error);
	success = false;
});

let success: boolean = $state(false);
</script>

<div class="m-2 mx-auto flex flex-col w-full items-center justify-center p-2 text-gray-700 dark:text-gray-400">
    {#if success}
        <div class="flex flex-row">
            <CheckCircleOutline size="xl" color="green" class="m-2"/>
            <div class="m-2 p-2">
                {$_('registration.emailValidationMessage')}
            </div>
        </div>
        <UserLogin/>
    {:else}
        <div class="flex flex-row">
        <ExclamationCircleOutline size="xl" color="red" class="m-2"/>
        <div class="m-2 p-2">
            {$_('registration.emailValidationError')}
        </div>
        </div>
    {/if}
</div>
