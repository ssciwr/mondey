<svelte:options runes={true}/>

<script lang="ts">
import ArrowUpDownOutline from "flowbite-svelte-icons/ArrowUpDownOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { buttonClasses } from "#lib/buttonClasses.ts";
import { i18n } from "#lib/i18n.svelte.ts";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button aria-roledescription={i18n.tr.admin.reorder} class={`${buttonClasses.secondary} ${buttonClasses.icon} rounded-lg!`} {onclick}>
    <ArrowUpDownOutline class="h-5 w-5"/>
</Button>
