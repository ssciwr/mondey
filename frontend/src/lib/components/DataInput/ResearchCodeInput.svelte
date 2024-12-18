<svelte:options runes={true} />

<script lang="ts">
import { verhoeff } from "cdigit";
import { Input } from "flowbite-svelte";
import { onMount } from "svelte";

let {
	value = $bindable(""),
	valid = $bindable(verhoeff.validate(value)),
}: {
	value: string;
	valid: boolean;
} = $props();

function validate(code: string) {
	valid = code === "" || (code.length === 6 && verhoeff.validate(code));
}

function oninput(event: Event) {
	const target = event.target as HTMLInputElement;
	validate(target.value);
}

onMount(() => {
	validate(value);
});
</script>

<div class="flex flex-row items-center">
	<Input type="text" bind:value class="mr-2" {oninput} color={valid ? 'base' : 'red'} data-testid="researchCodeInput"/>
</div>
