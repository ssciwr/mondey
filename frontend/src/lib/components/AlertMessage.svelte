<svelte:options runes={true} />
<script lang='ts'>
import { i18n } from "$lib/i18n.svelte";
import { Alert, Button } from "flowbite-svelte";
import { EyeSolid, InfoCircleSolid } from "flowbite-svelte-icons";

let {
	message = "",
	title = "",
	infotitle = "",
	lastpage = "",
	infopage = "",
	onclick = (event = undefined) => {
		console.log(event);
	},
}: {
	message?: string;
	title?: string;
	infotitle?: string;
	lastpage?: string;
	infopage?: string;
	onclick?: (event: Event | undefined) => void | Promise<void>;
} = $props();
</script>

<Alert class="m-4 p-4">
	<div class="flex items-center gap-3">
		<InfoCircleSolid class="h-5 w-5" />
		<span class="text-lg font-medium"> {title} </span>
	</div>
	<p class="mb-4 mt-2">{message}</p>
	<div class="flex gap-2">
		{#if infopage != ''}
			<Button size="md" href={infopage}><EyeSolid class="me-2 h-4 w-4" />{infotitle}</Button>
		{/if}
		<Button size="md" outline href={lastpage} on:click={onclick}>{i18n.tr.misc.understood}</Button>
	</div>
</Alert>
