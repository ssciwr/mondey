<svelte:options runes={true} />

<script lang="ts">
import { Input } from "flowbite-svelte";

let {
	value = null,
	outerClass = "space-y-4",
	innerClass = null,
	disabled = false,
	required = true,
}: {
	value: string | null;
	outerClass: string | null;
	innerClass: string | null;
	disabled: boolean;
	required: boolean;
} = $props();
</script>

<div class={outerClass}>
    <Input type="date" bind:value class={innerClass} {required} {disabled} />
</div>
