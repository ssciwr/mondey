<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Button, Modal } from "flowbite-svelte";
import ExclamationCircleOutline from "flowbite-svelte-icons/ExclamationCircleOutline.svelte";

let {
	open = $bindable(false),
	onclick,
}: { open: boolean; onclick: () => void } = $props();
</script>

<Modal bind:open size="xs" autoclose>
	<div class="text-center">
		<ExclamationCircleOutline class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-200" />
		<h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
			{i18n.tr.admin.deleteAreYouSure}
		</h3>
		<Button color="red" class="me-2" {onclick}>
			{i18n.tr.admin.yesSure}
		</Button>
		<Button color="alternative">{i18n.tr.admin.noCancel}</Button>
	</div>
</Modal>
