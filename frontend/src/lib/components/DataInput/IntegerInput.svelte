<svelte:options runes={true} />

<script lang="ts">
import { Input } from "flowbite-svelte";
import { isValidAge } from "#lib/util.ts";

let {
	value = $bindable(),
	min = 0,
	max = 72,
}: {
	value: number;
	min?: number;
	max?: number;
} = $props();

let valid = $derived(isValidAge(value) && value >= min && value <= max);
</script>

<Input type="number" {min} {max} bind:value={value} color={valid ? 'default' : 'red'}/>
