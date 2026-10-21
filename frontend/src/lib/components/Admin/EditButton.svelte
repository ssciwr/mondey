<svelte:options runes={true} />

<script lang="ts">
import { Tooltip } from "flowbite-svelte";
import EditOutline from "flowbite-svelte-icons/EditOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { buttonClasses } from "#lib/buttonClasses.ts";
import { i18n } from "#lib/i18n.svelte.ts";

let {
	onclick,
	dataTestid = undefined,
}: { onclick: (event: Event) => void; dataTestid?: string } = $props();
</script>


<Button class={`${buttonClasses.secondary} ${buttonClasses.icon}`} aria-roledescription={i18n.tr.admin.edit} data-testid={dataTestid} {onclick}><EditOutline class="h-5 w-5" /></Button>
<Tooltip class={`${buttonClasses.tooltip} -ml-2.5`}>{i18n.tr.admin.edit}</Tooltip>
