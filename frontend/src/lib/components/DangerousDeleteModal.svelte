<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Button, Input, Label, Modal, Spinner } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";
import { onMount } from "svelte";

type DeletionWillAffectTotals = {
	[key: string]: number;
};

type DryRunnableDataResponse =
	| {
			data: { deletion_executed: boolean; error?: never; would_delete?: never };
	  }
	| {
			data: {
				would_delete: DeletionWillAffectTotals;
				error?: never;
				deletion_executed?: never;
			};
	  }
	| { error: string };

let {
	open = $bindable(false),
	deleteDryRunnableRequest,
	afterDelete,
	intendedConfirmCode,
}: {
	open: boolean;
	deleteDryRunnableRequest: (
		dryRun: boolean,
	) => Promise<DryRunnableDataResponse>;
	afterDelete: () => void;
	intendedConfirmCode: string;
} = $props();

let deletionWillAffectTotals = $state<DeletionWillAffectTotals>({});
let deleteConfirmCode: string = $state("");
let deleteDone: boolean = $state(false);

let sendDeleteRequest = async () => {
	if (deleteConfirmCode === intendedConfirmCode) {
		const { data, error } = await deleteDryRunnableRequest(false);
		console.error("Error on real call:", error);

		if (data.deletion_executed) {
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
		const { data, error } = await deleteDryRunnableRequest(true);
		if (error) {
			alertStore.showAlert(i18n.tr.admin.deleteError, "", true, false);
			console.error(error);
		}
		if (data.would_delete) {
			deletionWillAffectTotals = data.would_delete;
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

        {#if Object.keys(deletionWillAffectTotals).length == 0}
            <div>
                <Spinner />
            </div>
        {:else}
            {i18n.tr.admin.deletionWillAffect}
            <div class="text-black" style="background-color:rgb(255,220,220);border: 2px solid darkred;border-radius:10px;padding:10px">
                <ul>
                    {#each Object.entries(deletionWillAffectTotals) as [translationKey, total]}
                        <li>{total} {translationKey}</li>
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

        <Button color="alternative">{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
