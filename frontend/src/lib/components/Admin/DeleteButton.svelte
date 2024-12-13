<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import TrashBinOutline from "flowbite-svelte-icons/TrashBinOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button color="red" {onclick}><TrashBinOutline class="me-2 h-5 w-5" /> {i18n.tr.admin.delete}</Button>
