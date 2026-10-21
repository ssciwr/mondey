<svelte:options runes={true} />

<script lang="ts">
import { buttonClasses } from "$lib/buttonClasses";
import { i18n } from "$lib/i18n.svelte";
import { Tooltip } from "flowbite-svelte";
import TrashBinOutline from "flowbite-svelte-icons/TrashBinOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button class={`${buttonClasses.danger} ${buttonClasses.icon}`} aria-roledescription={i18n.tr.admin.delete} {onclick}><TrashBinOutline class="h-5 w-5" /></Button>
<Tooltip class={buttonClasses.tooltip}>{i18n.tr.admin.delete}</Tooltip>
