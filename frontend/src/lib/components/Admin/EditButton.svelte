<svelte:options runes={true} />

<script lang="ts">
import EditOutline from "flowbite-svelte-icons/EditOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { _ } from "svelte-i18n";

let {
	onclick,
	disabled = false,
}: { onclick: (event: Event) => void; disabled: boolean } = $props();
</script>

<Button color="yellow" {onclick} {disabled}><EditOutline class="me-2 h-5 w-5" /> {$_('admin.edit')}</Button>
