<svelte:options runes={true} />

<script lang="ts">
import type { DeleteResponse } from "$lib/client";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Button, Input, Label, Modal, Spinner } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	deleteDryRunnableRequest,
	afterDelete,
	intendedConfirmCode,
}: {
	open: boolean;
	deleteDryRunnableRequest: (dryRun: boolean) => Promise<DeleteResponse>;
	afterDelete: () => void;
	intendedConfirmCode: string;
} = $props();

let deletionWillAffectTotals = $state<DeleteResponse["children"]>({});
let deleteConfirmCode: string = $state("");
let deleteDone: boolean = $state(false);

let sendDeleteRequest = async () => {
	if (deleteConfirmCode === intendedConfirmCode) {
		const resp = await deleteDryRunnableRequest(false);
		const { ok, dry_run, children, error } = resp.data;

		if (ok && dry_run === false) {
			deleteDone = true;
			afterDelete(); // refresh the list items this is in etc.
		} else {
			alertStore.showAlert(i18n.tr.admin.deleteError, error, true, false);
			console.error(error);
		}
	}
};

$effect(async () => {
	if (open) {
		const resp = await deleteDryRunnableRequest(true);
		const { children, error } = resp.data;
		if (error) {
			alertStore.showAlert(i18n.tr.admin.deleteError, "", true, false);
		}
		if (children) {
			deletionWillAffectTotals = children;
		}
	} else {
		deletionWillAffectTotals = {};
		deleteDone = false;
		deleteConfirmCode = "";
	}
});
</script>

<Modal bind:open size="xs" autoclose>
    <div class="text-center">
        {#if deleteDone}
            <h3><CheckCircleOutline class="h-12 w-12" />{i18n.tr.admin.deletionComplete}</h3>
        {/if}

        <ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {i18n.tr.admin.deleteAreYouSure}
        </h3>

        {#if Object.keys(deletionWillAffectTotals).length === 0}
            <div class="mb-6">
                <Spinner />
            </div>
        {:else}
            {i18n.tr.admin.deletionWillAffect}
            <div class="text-black" style="background-color:rgb(255,220,220);border: 2px solid darkred;border-radius:10px;padding:10px">
                <ul>
                    {#each Object.entries(deletionWillAffectTotals) as [translationKey, total]}
                        <li>{total} {i18n.tr.admin && translationKey in i18n.tr.admin
                            ? i18n.tr.admin[translationKey] : i18n.tr.admin.affectedAnswers}</li>
                    {/each}
                </ul>
            </div>

            <div class="mt-10 mb-5">
            {i18n.tr.admin.deletionConfirm}: <code>{intendedConfirmCode}</code>

            <Label
                    for={"password"}
                    class="font-semibold text-gray-700 dark:text-gray-400"
            >{i18n.tr.admin.enterDeletionConfirmation}</Label>

            <Input id="confirm-delete"  bind:value={deleteConfirmCode}></Input>
            </div>

            <Button color="red" class="me-2" disabled={intendedConfirmCode !== deleteConfirmCode} on:click={sendDeleteRequest}>
            {i18n.tr.admin.yesSure}
            </Button>
        {/if}

        <Button class="btn-secondary">{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
