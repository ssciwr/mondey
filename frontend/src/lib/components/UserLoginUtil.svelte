<script lang="ts">
import { base } from "$app/paths";
import { Checkbox } from "flowbite-svelte";
export let cls = "";
export let checked = false;
export let onchecked = (event) => {};
export let onchange = (event) => {};
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
