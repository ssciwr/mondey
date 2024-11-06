<svelte:options runes={true} />

<script lang="ts">
import TrashBinOutline from "flowbite-svelte-icons/TrashBinOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { _ } from "svelte-i18n";

let {
	onclick,
	disabled = false,
}: { onclick: (event: Event) => void; disabled: boolean } = $props();
</script>

<Button color="red" {onclick} {disabled}><TrashBinOutline class="me-2 h-5 w-5" /> {$_('admin.delete')}</Button>
