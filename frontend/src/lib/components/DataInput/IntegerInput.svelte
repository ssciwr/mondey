<svelte:options runes={true} />

<script lang="ts">
import { isValidAge } from "$lib/util";
import { Input } from "flowbite-svelte";

let {
	value = $bindable(),
	min = 0,
	max = 72,
}: {
	value: number;
	min?: number;
	max?: number;
} = $props();

let valid = $derived(isValidAge(value));
</script>

<Input type="number" {min} {max} bind:value={value} color={valid ? 'base' : 'red'}/>
