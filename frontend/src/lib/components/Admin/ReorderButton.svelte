<svelte:options runes={true}/>

<script lang="ts">
import ArrowUpDownOutline from "flowbite-svelte-icons/ArrowUpDownOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { _ } from "svelte-i18n";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button color="purple" {onclick}>
    <ArrowUpDownOutline class="me-2 h-5 w-5"/> {$_('admin.reorder')}
</Button>
