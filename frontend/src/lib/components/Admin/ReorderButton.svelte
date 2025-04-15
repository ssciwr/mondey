<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import ArrowUpDownOutline from "flowbite-svelte-icons/ArrowUpDownOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button aria-roledescription={i18n.tr.admin.reorder} class="btn-secondary btn-icon btn-icon-rounded" {onclick}>
    <ArrowUpDownOutline class="h-5 w-5"/>
</Button>
