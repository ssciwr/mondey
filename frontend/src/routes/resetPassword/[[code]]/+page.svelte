<svelte:options runes={true} />
<script lang="ts">
import { page } from "$app/stores";
import { resetResetPassword } from "$lib/client/services.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import { i18n } from "$lib/i18n.svelte";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Input } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let pw = $state("");
let confirmPw = $state("");
let showAlert = $state(false);
let alertMessage = $state(i18n.tr.forgotPw.confirmError);
let success: boolean = $state(false);

onMount(() => {
	if (
		$page.params.code === undefined ||
		$page.params.code === null ||
		$page.params.code === ""
	) {
		alertMessage = i18n.tr.forgotPw.codeError;
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
	alertMessage = i18n.tr.forgotPw.sendError;
	showAlert = true;
	success = false;
}
</script>

{#if showAlert === true}
    <AlertMessage title={i18n.tr.forgotPw.error} message={alertMessage} onclick={() => {
        showAlert = false;
    }}/>
{:else}
    {#if success === true}
        <div class="flex flex-row">
            <CheckCircleOutline size="xl" color="green" class="m-2"/>
            <div class="m-2 p-2">
                {i18n.tr.forgotPw.successReset}
            </div>
        </div>
        <Button href="/userLand/userLogin" size="md">{i18n.tr.forgotPw.goToLogin}</Button>
    {:else}
    <Card class="container m-2 mx-auto w-full max-w-xl items-center justify-center p-2">

        <Heading
            tag="h3"
            class="m-2 p-2 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
            >{i18n.tr.forgotPw.resetHeading}</Heading>

        <form onsubmit={preventDefault(submitData)} class = "space-y-4">
            <div class="m-2 mx-auto w-full flex-col space-y-6 p-2">

                <DataInput component = {Input} bind:value={pw} required={true} id="restPw" kwargs={{type: "password"}} label={i18n.tr.forgotPw.inputLabelPw}/>

                <DataInput component = {Input} bind:value={confirmPw} required={true} id="restConfirmPw" kwargs={{type: "password"}} label={i18n.tr.forgotPw.inputlabelPwConfirm}/>
            </div>
			<div class="m-2 flex w-full items-center justify-center p-2">
                <Button size="md" type="submit">{i18n.tr.forgotPw.pending}</Button>
            </div>
        </form>
    </Card>
    {/if}
{/if}
