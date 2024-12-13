<svelte:options runes={true}/>

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import ArrowUpDownOutline from "flowbite-svelte-icons/ArrowUpDownOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button color="purple" {onclick}>
    <ArrowUpDownOutline class="me-2 h-5 w-5"/> {i18n.tr.admin.reorder}
</Button>
