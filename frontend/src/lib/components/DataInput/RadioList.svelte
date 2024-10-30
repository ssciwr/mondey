<script lang="ts">
import { Radio, RadioButton } from "flowbite-svelte";
import { createEventDispatcher } from "svelte";

const dispatch = createEventDispatcher();

function handleChange(event) {
	dispatch("change", { value: event.target.value });
}

function handleBlur(event) {
	dispatch("blur", { value: event.target.value });
}

function handleClick(event) {
	dispatch("click", { value: event.target.value });
}
export let value: any;
export let disabled = false;
export let required = true;
let windowWidth = 1920;
$: smallScreen = windowWidth < 800;
</script>

<svelte:window bind:innerWidth={windowWidth} />

<div class="grid w-full grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
	{#if smallScreen}
		{#each $$props.items as item}
			<RadioButton
				class="mx-2"
				{disabled}
				{required}
				bind:group={value}
				value={item.value}
				on:change={handleChange}
				on:blur={handleBlur}
				on:click={handleClick}>{item.label}</RadioButton
			>
		{/each}
	{:else}
		{#each $$props.items as item}
			<Radio
				class="mx-2"
				{disabled}
				{required}
				bind:group={value}
				value={item.value}
				on:change={handleChange}
				on:blur={handleBlur}
				on:click={handleClick}>{item.label}</Radio
			>
		{/each}
	{/if}
</div>
