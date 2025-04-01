<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import CheckOutline from "flowbite-svelte-icons/CheckOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let {
	onclick,
	text = i18n.tr.admin.saveChanges,
	disabled = false,
}: { onclick: () => void; text?: string; disabled?: boolean } = $props();
</script>

<Button class="btn-secondary" {onclick} {disabled}
>
    <CheckOutline class="me-2 h-5 w-5"/> {text}
</Button>
