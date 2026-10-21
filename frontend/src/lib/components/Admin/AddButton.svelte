<svelte:options runes={true} />

<script lang="ts">
import PlusOutline from "flowbite-svelte-icons/PlusOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { buttonClasses } from "#lib/buttonClasses.ts";
import { i18n } from "#lib/i18n.svelte.ts";

let {
	onclick,
	disabled = false,
}: { onclick: (event: Event) => void; disabled?: boolean } = $props();
</script>

<Button class={buttonClasses.primary} {onclick} {disabled}
	><PlusOutline class="me-2 h-5 w-5" /> {i18n.tr.admin.add}</Button
>
