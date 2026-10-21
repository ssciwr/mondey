<svelte:options runes={true} />
<script lang='ts'>
import { Alert, Button } from "flowbite-svelte";
import {
	ExclamationCircleSolid,
	EyeSolid,
	InfoCircleSolid,
} from "flowbite-svelte-icons";
import { buttonClasses } from "#lib/buttonClasses.ts";
import { i18n } from "#lib/i18n.svelte.ts";

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

const color = isError ? "red" : "blue";
</script>

<Alert color={color} border id={`${id}`} class="m-4 p-6">

	<div class="mb-4 mt-2" >
		{#if isError}
			<ExclamationCircleSolid class="inline" />
		{:else}
			<InfoCircleSolid class="inline" />
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
		{#if infopage !== ''}
			<Button class={`${isError ? buttonClasses.danger : buttonClasses.primary} ${buttonClasses.large}`} href={infopage}><EyeSolid class="me-2 h-4 w-4" />{infotitle}</Button>
		{/if}
		<Button class={`${isError ? buttonClasses.danger : buttonClasses.primary} ${buttonClasses.large}`} href={lastpage} {onclick}>
			{i18n.tr.misc.understood}
		</Button>
	</div>
</Alert>
