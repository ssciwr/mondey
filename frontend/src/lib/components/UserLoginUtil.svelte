<svelte:options runes={true} />
<script lang="ts">
import { base } from "$app/paths";
import { Checkbox } from "flowbite-svelte";

let {
	cls = "",
	checked = false,
	onchecked = (event) => {
		console.log("empty onchecked: ", event);
	},
	onchange = (event) => {
		console.log("empty onchange: ", event);
	},
}: {
	cls?: string;
	checked?: boolean;
	onchecked?: (event: Event) => void;
	onchange?: (event: Event) => void;
} = $props();
</script>

<div class={'container mx-auto flex w-full max-w-md items-start' + cls}>
	<Checkbox bind:checked on:click={onchecked} on:change={onchange}>Remember me</Checkbox>
	<a
		href={`${base}/userLand/lostPassword`}
		class="ms-auto text-primary-700 hover:underline dark:text-primary-500"
	>
		Lost password?
	</a>
</div>
