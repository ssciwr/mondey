<svelte:options runes={true} />

<script lang="ts">
    import { i18n } from "$lib/i18n.svelte";
    import { Button, Modal } from "flowbite-svelte";
    import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";

    let {
        open = $bindable(false),
        filename = $bindable(""),
        onConfirm,
        onCancel
    }: {
        open: boolean;
        filename: string;
        onConfirm: () => void;
        onCancel: () => void;
    } = $props();
</script>

<Modal bind:open size="xs" autoclose>
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
            {filename ? `${i18n.tr.admin.confirmImport} "${filename}"?` : i18n.tr.admin.confirmImport}
        </h3>
        <Button color="blue" class="me-2" onclick={onConfirm} data-testid="confirm-import-btn">
            {i18n.tr.admin.yes}
        </Button>
        <Button color="alternative" onclick={onCancel}>{i18n.tr.admin.noCancel}</Button>
    </div>
</Modal>