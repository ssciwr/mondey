<svelte:options runes={true} />
<script lang="ts">
import { page } from "$app/stores";
import { resetResetPassword } from "$lib/client/services.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

let pw = $state("");
let confirmPw = $state("");
let showAlert = $state(false);
let alertMessage = $state($_("forgotPw.confirmError"));
let success: boolean = $state(false);

onMount(() => {
	if (
		$page.params.code === undefined ||
		$page.params.code === null ||
		$page.params.code === ""
	) {
		alertMessage = $_("forgotPw.codeError");
		showAlert = true;
	}
});

async function submitData(): Promise<void> {
	if (pw !== confirmPw) {
		showAlert = true;
		return;
	}

	const { data, error } = await resetResetPassword({
		body: { token: $page.params.code, password: pw },
	});

	if ((!error && data) || error?.detail === "VERIFY_USER_ALREADY_VERIFIED") {
		success = true;
		return;
	}

	console.log(error);
	alertMessage = $_("forgotPw.sendError");
	showAlert = true;
	success = false;
}
</script>

{#if showAlert === true}
    <AlertMessage title={$_('forgotPw.Error')} message={alertMessage} onclick={() => {
        showAlert = false;
    }}/>
{:else}
    {#if success === true}
        <div class="flex flex-row">
            <CheckCircleOutline size="xl" color="green" class="m-2"/>
            <div class="m-2 p-2">
                {$_('forgotPw.successReset')}
            </div>
        </div>
        <Button href="/userLand/userLogin" size="md">{$_('forgotPw.goToLogin')}</Button>
    {:else}
    <Card class="container m-2 mx-auto w-full max-w-xl items-center justify-center p-2">

        <Heading
            tag="h3"
            class="m-2 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
            >{$_('forgotPw.resetHeading')}</Heading>

        <form onsubmit={preventDefault(submitData)} class = "space-y-4">
            <div class="m-2 mx-auto w-full flex-col space-y-6 p-2">

                <DataInput component = {Input} bind:value={pw} required={true} id="restPw" kwargs={{type: "password"}} label={$_("forgotPw.inputlabelPw")}/>

                <DataInput component = {Input} bind:value={confirmPw} required={true} id="restConfirmPw" kwargs={{type: "password"}} label={$_("forgotPw.inputlabelPwConfirm")}/>
            </div>
			<div class="m-2 flex w-full items-center justify-center p-2">
                <Button size="md" type="submit">{$_('forgotPw.pending')}</Button>
            </div>
        </form>
    </Card>
    {/if}
{/if}
