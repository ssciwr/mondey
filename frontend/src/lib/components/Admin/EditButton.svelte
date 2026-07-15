<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Tooltip } from "flowbite-svelte";
import EditOutline from "flowbite-svelte-icons/EditOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let {
	onclick,
	dataTestid = undefined,
}: { onclick: (event: Event) => void; dataTestid?: string } = $props();
</script>


<Button class="btn-secondary btn-icon" aria-roledescription={i18n.tr.admin.edit} data-testid={dataTestid} {onclick}><EditOutline class="h-5 w-5" /></Button>
<Tooltip class="btn-secondary btn-icon" style="margin-left:-10px">{i18n.tr.admin.edit}</Tooltip>
