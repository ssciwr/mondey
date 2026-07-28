<svelte:options runes={true}/>

<script lang="ts">
import type { DeleteResponse } from "$lib/client";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Button, Input, Label, Modal, Spinner } from "flowbite-svelte";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";

type DeleteRequestResult = {
	data?: unknown;
	error?: unknown;
};

let {
	open = $bindable(false),
	deleteRequest,
	afterDelete,
}: {
	open: boolean;
	deleteRequest: (
		dryRun: boolean,
		password: string,
	) => Promise<DeleteRequestResult> | undefined;
	afterDelete: () => void;
} = $props();

let deletionWillAffectTotals = $state<DeleteResponse["children"]>({});
let password: string = $state("");
let deletionInProgress: boolean = $state(false);

let settingsText = $derived(i18n.tr.settings as Record<string, string>);

let sendDeleteRequest = async () => {
	if (password === "") {
		return;
	}
	deletionInProgress = true;
	const resp = await deleteRequest(false, password);
	const data = (resp?.data ?? {}) as Partial<DeleteResponse>;

	if (resp && !resp.error && data.ok && data.dry_run === false) {
		open = false;
		afterDelete();
	} else {
		alertStore.showAlert(
			i18n.tr.settings.alertTitle,
			i18n.tr.settings.deleteAccountError,
			true,
			false,
		);
		console.error(resp?.error);
	}
	deletionInProgress = false;
};

$effect(() => {
	if (!open) {
		deletionWillAffectTotals = {};
		password = "";
		deletionInProgress = false;
		return;
	}
	let cancelled = false;
	void (async () => {
		// a dry run first, so that the user is told what they are about to lose
		const resp = await deleteRequest(true, "");
		if (cancelled) {
			return;
		}
		if (!resp || resp.error) {
			alertStore.showAlert(
				i18n.tr.settings.alertTitle,
				i18n.tr.settings.deleteAccountError,
				true,
				false,
			);
			return;
		}
		const { children } = (resp.data ?? {}) as Partial<DeleteResponse>;
		if (children) {
			deletionWillAffectTotals = children;
		}
	})();
	return () => {
		cancelled = true;
	};
});
</script>

<Modal bind:open size="xs" id="deleteAccountModal">
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200"/>
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {i18n.tr.settings.deleteAccountAreYouSure}
        </h3>

        {#if Object.keys(deletionWillAffectTotals).length === 0}
            <div class="mb-6">
                <Spinner/>
            </div>
        {:else}
            {i18n.tr.settings.deleteAccountWillAffect}
            <div class="text-black"
                 style="background-color:rgb(255,220,220);border: 2px solid darkred;border-radius:10px;padding:10px">
                <ul>
                    {#each Object.entries(deletionWillAffectTotals) as [translationKey, total]}
                        <li>{total} {settingsText?.[translationKey] ?? translationKey}</li>
                    {/each}
                </ul>
            </div>

            <p class="mt-5">{i18n.tr.settings.deleteAccountIrreversible}</p>

            <div class="mt-6 mb-5">
                <Label
                        for="deleteAccountPassword"
                        class="font-semibold text-gray-700 dark:text-gray-400"
                >{i18n.tr.settings.deleteAccountEnterPassword}</Label>

                <Input
                        id="deleteAccountPassword"
                        bind:value={password}
                        type="password"
                        autocomplete="current-password"
                        placeholder={i18n.tr.settings.placeholder}
                />
            </div>

            <Button color="red" class="me-2" disabled={password === "" || deletionInProgress}
                    on:click={sendDeleteRequest}>
                {#if deletionInProgress}
                    <Spinner class="me-2" size="4"/>
                {/if}
                {i18n.tr.settings.deleteAccountConfirm}
            </Button>
        {/if}

        <Button class="btn-secondary" on:click={() => {open = false;}}
        >{i18n.tr.settings.deleteAccountCancel}</Button>
    </div>
</Modal>
