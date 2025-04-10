<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Button, Input, Modal, Spinner } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";
import { onMount } from "svelte";

type DeletionWillAffectTotals = {
    [key: string]: number;
};

type DryRunnableDataResponse = 
    | { deletion_executed: boolean; error?: never; would_delete?: never }
    | { would_delete: DeletionWillAffectTotals; error?: never; deletion_executed?: never }
    | { error: string; deletion_executed?: never; would_delete?: never };

let {
	open = $bindable(false),
	deleteDryRunnableRequest,
	intendedConfirmCode,
}: {
	open: boolean;
	deleteDryRunnableRequest: (dryRun: boolean) => Promise<DryRunnableDataResponse>;
	intendedConfirmCode: string;
} = $props();

let deletionWillAffectTotals = $state<DeletionWillAffectTotals>({});
let deleteConfirmCode: string = $state("");
let deleteDone: boolean = $state(false);

let sendDeleteRequest = async () => {
	// if confirm text is what we expect..
	// then call deleteDryRunnableRequest(false) // dry run false.
	// otherwise display an alert.
	if (deleteConfirmCode === intendedConfirmCode) {
		const result = await deleteDryRunnableRequest(false);
		if (result.deletion_executed) {
			deleteDone = true;
		} else {
			alertStore.showAlert(i18n.tr.admin.deleteError, "", true, false);
			console.error(result.error);
		}
	}
};

onMount(async () => {
	const dryRunResult = await deleteDryRunnableRequest(true);
	if ('would_delete' in dryRunResult) {
		deletionWillAffectTotals = dryRunResult.would_delete;
		intendedConfirmCode = Object.keys(deletionWillAffectTotals)[0];
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
            <Spinner />
        {:else}
            {i18n.tr.admin.deletionWillAffect}
            <ul>
                {#each Object(deletionWillAffectTotals).keys() as { translationKey}}
                    {i18n.tr.admin.deletion[translationKey]} x {deletionWillAffectTotals[translationKey]}
                {/each}
            </ul>

            {i18n.tr.admin.deletionWillAffect}: <code>{intendedConfirmCode}</code>

            <Input bind:value={deleteConfirmCode}></Input>

            <Button color="red" class="me-2" on:click={sendDeleteRequest}>
            {i18n.tr.admin.yesSure}
            </Button>
        {/if}

        <Button color="alternative">{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
