<svelte:options runes={true} />

<script lang="ts">
import CheckOutline from "flowbite-svelte-icons/CheckOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { _ } from "svelte-i18n";

let { onclick, disabled = false }: { onclick: () => void; disabled?: boolean } =
	$props();
</script>

<Button color="green" {onclick} {disabled}
	><CheckOutline class="me-2 h-5 w-5" /> {$_('admin.save-changes')}</Button
>
