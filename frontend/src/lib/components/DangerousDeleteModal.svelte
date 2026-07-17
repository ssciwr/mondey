<svelte:options runes={true}/>

<script lang="ts">
import type { DeleteResponse } from "$lib/client";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Button, Input, Label, Modal, Spinner } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";

// Callers hand us an SDK delete call, which resolves to the client's
// `{ data, error }` envelope rather than a bare DeleteResponse. Endpoints that
// declare no response schema (e.g. documents) resolve `data` as `unknown`, and
// Questions' callback returns undefined when nothing is selected, so both are
// narrowed below.
type DeleteRequestResult = {
	data?: unknown;
	error?: unknown;
};

let {
	open = $bindable(false),
	deleteDryRunnableRequest,
	afterDelete,
	intendedConfirmCode,
}: {
	open: boolean;
	deleteDryRunnableRequest: (
		dryRun: boolean,
	) => Promise<DeleteRequestResult> | undefined;
	afterDelete: () => void;
	intendedConfirmCode: string;
} = $props();

let deletionWillAffectTotals = $state<DeleteResponse["children"]>({});

// The affected-totals keys come from the API, so index the admin section through
// the dynamic view rather than naming each key.
let adminText = $derived(i18n.tr.admin as Record<string, string> | undefined);
let deleteConfirmCode: string = $state("");
let deleteDone: boolean = $state(false);

let sendDeleteRequest = async () => {
	if (deleteConfirmCode !== intendedConfirmCode) {
		return;
	}
	const resp = await deleteDryRunnableRequest(false);
	const data = (resp?.data ?? {}) as Partial<DeleteResponse>;
	// Deletions like Admin Documents report no dry_run field, so treat a missing
	// one as a real deletion.
	const dry_run = data.dry_run ?? false;

	if (resp && !resp.error && data.ok && dry_run === false) {
		deleteDone = true;
		afterDelete(); // refresh the list items this is in etc.
	} else {
		alertStore.showAlert(i18n.tr.admin.deleteError, "", true, false);
		console.error(resp?.error);
	}
};

$effect(() => {
	if (!open) {
		deletionWillAffectTotals = {};
		deleteDone = false;
		deleteConfirmCode = "";
		return;
	}
	// The dry run is async, so guard against a stale response arriving after the
	// modal has closed or been reopened for a different item.
	let cancelled = false;
	void (async () => {
		const resp = await deleteDryRunnableRequest(true);
		if (cancelled) {
			return;
		}
		if (!resp || resp.error) {
			alertStore.showAlert(i18n.tr.admin.deleteError, "", true, false);
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

<Modal bind:open size="xs" autoclose>
    <div class="text-center">
        {#if deleteDone}
            <h3>
                <CheckCircleOutline class="h-12 w-12"/>{i18n.tr.admin.deletionComplete}</h3>
        {/if}

        <ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200"/>
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {i18n.tr.admin.deleteAreYouSure}
        </h3>

        {#if Object.keys(deletionWillAffectTotals).length === 0}
            <div class="mb-6">
                <Spinner/>
            </div>
        {:else}
            {i18n.tr.admin.deletionWillAffect}
            <div class="text-black"
                 style="background-color:rgb(255,220,220);border: 2px solid darkred;border-radius:10px;padding:10px">
                <ul>
                    {#each Object.entries(deletionWillAffectTotals) as [translationKey, total]}
                        <li>{total} {adminText?.[translationKey] ?? i18n.tr.admin.affectedAnswers}</li>
                    {/each}
                </ul>
            </div>

            <div class="mt-10 mb-5">
                <p>{i18n.tr.admin.deletionConfirm}:</p>
                <div class="mb-5 p-3 rounded-xl" style="background-color:rgba(127,127,127,0.3)">
                    <b>{intendedConfirmCode}</b></div>

                <Label
                        for={"password"}
                        class="font-semibold text-gray-700 dark:text-gray-400"
                >{i18n.tr.admin.enterDeletionConfirmation}</Label>

                <Input id="confirm-delete" bind:value={deleteConfirmCode}></Input>
            </div>

            <Button color="red" class="me-2" disabled={intendedConfirmCode !== deleteConfirmCode}
                    on:click={sendDeleteRequest}>
                {i18n.tr.admin.yesSure}
            </Button>
        {/if}

        <Button class="btn-secondary">{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
