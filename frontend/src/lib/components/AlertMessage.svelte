<script>
import { Alert, Button } from "flowbite-svelte";
import { EyeSolid, InfoCircleSolid } from "flowbite-svelte-icons";

export let message = "";
export let title = "";
export let infotitle = "";
export let lastpage = "";
export let infopage = "";
export let onclick = () => {};
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
		<Button size="md" outline href={lastpage} on:click={onclick}>Verstanden</Button>
	</div>
</Alert>
