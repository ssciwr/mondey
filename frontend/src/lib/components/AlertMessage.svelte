<svelte:options runes={true} />
<script lang='ts'>
import { i18n } from "$lib/i18n.svelte";
import {Alert} from "flowbite-svelte";
import { EyeSolid, InfoCircleSolid, ExclamationCircleSolid } from "flowbite-svelte-icons";

let {
	id = "alertMessage",
	message = "",
	title = "",
	infotitle = "",
	lastpage = "",
	infopage = "",
	isError = false,
	onclick = (event = undefined) => {
		console.log(event);
	},
}: {
	id?: string;
	message?: string;
	title?: string;
	infotitle?: string;
	lastpage?: string;
	infopage?: string;
	isError?: boolean; // We keep this as an optional prop for backward compatibility with existing <AlertMessage> usage.
	onclick?: (event: Event | undefined) => void | Promise<void>;
} = $props();

const color = isError ? 'red' : 'blue'
</script>

<Alert color={color} border id={`${id}`} class="m-4 p-6">

	<div class="mb-4 mt-2" >
		{#if isError}
			<ExclamationCircleSolid style="display:inline" />
		{:else}
			<InfoCircleSolid style="display:inline" />
		{/if}
		&nbsp;
		<span class="text-lg font-medium">
			{title}
		</span>
		<p>
	 		{message}
		</p>
	</div>
	<div class="flex gap-2">
		{#if infopage != ''}
			<a class={(isError) ? "btn-danger" : "btn-primary-alt"} href={infopage}><EyeSolid class="me-2 h-4 w-4" />{infotitle}</a>
		{/if}
		<a class={(isError) ? "btn-danger" : "btn-primary-alt"} href={lastpage} on:click={onclick}>
			{i18n.tr.misc.understood}
		</a>
	</div>
</Alert>
