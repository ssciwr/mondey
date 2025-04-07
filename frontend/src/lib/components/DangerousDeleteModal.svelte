<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Button, Input, Modal, Spinner } from "flowbite-svelte";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	deleteDryRunnableRequest,
}: {
	open: boolean;
	deleteDryRunnableRequest: (b: boolean) => {
		would_delete: { translation_key: number } | { deletion_executed: boolean };
	};
} = $props();

// todo: Type these better
let deletionWillAffectTotals = $state({});
let deleteConfirmCode: string = $state("");
let intendedConfirmCode: string = $state("");
let deleteDone: boolean = $state(false);

let sendDeleteRequest = () => {
	// if confirm text is what we expect..
	// then call deleteDryRunnableRequest(false) // dry run false.
	// otherwise display an alert.
	if (deleteConfirmCode === intendedConfirmCode) {
		const result: { deletion_executed: boolean } =
			deleteDryRunnableRequest(false);
		if (result.deletion_executed) {
			deleteDone = true;
		}
	}
};

onMount(() => {
	deletionWillAffectTotals = deleteDryRunnableRequest(true).would_delete; // dry run delete will return
	intendedConfirmCode = Object.keys(deletionWillAffectTotals)[0];
});
</script>

<Modal bind:open size="xs" autoclose>
    <div class="text-center">
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

            <Button color="red" class="me-2" onclick={sendDeleteRequest}>
            {i18n.tr.admin.yesSure}
            </Button>
        {/if}

        <Button color="alternative">{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>
