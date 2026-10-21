<svelte:options runes={true}/>

<script lang="ts">
import CheckOutline from "flowbite-svelte-icons/CheckOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { buttonClasses } from "#lib/buttonClasses.ts";
import { i18n } from "#lib/i18n.svelte.ts";

let {
	onclick,
	text = i18n.tr.admin.saveChanges,
	disabled = false,
}: {
	onclick: () => unknown;
	text?: string;
	disabled?: boolean;
} = $props();

// disabled while saving, so that a double click doesn't save twice
let saving = $state(false);

async function save() {
	saving = true;
	try {
		await onclick();
	} finally {
		saving = false;
	}
}
</script>

<Button class={buttonClasses.secondary} onclick={save} disabled={disabled || saving}
>
    <CheckOutline class="me-2 h-5 w-5"/> {text}
</Button>
