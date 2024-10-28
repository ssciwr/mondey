<svelte:options runes={true} />

<script lang="ts">
	// README: wrt event handlers: in svelte 5 there is a better solution to this, but since we don´t have this yet and
	// the svelte 4 solution requires a lot of boilerplate code (https://github.com/sveltejs/svelte/issues/2837#issuecomment-1848225140)
	// currently there are some hardcoded event handlers

	import { Label, Textarea } from 'flowbite-svelte';

	// variables
	// Simplify this as much as possible
	let component: any = $state();
	let value: any = $state();
	let label: string | null = $state(null);
	let componentClass: string = $state('');
	let textTrigger: string = $state('noAdditionalText');
	let additionalInput: any = $state(null);
	let properties: any = $state({});
	let eventHandlers = $state({});
	let additionalEventHandlers = $state({});
	let showTextField: boolean = $derived(checkShowTextfield(value));

	// functionality for showing the textfield when the trigger is selected
	function checkShowTextfield(v: any): boolean {
		if (v instanceof Array) {
			return v.includes(textTrigger);
		} else {
			return v === textTrigger;
		}
	}
</script>

{#if label}
	<Label for={properties.id} class="font-semibold text-gray-700 dark:text-gray-400">{label}</Label>
{/if}

<div class="space-y-4">
	<svelte:component
		this={component}
		class={highlight
			? 'border-primary-600 dark:border-primary-600 rounded border-2 ' + componentClass
			: componentClass}
		bind:value
		{...properties}
		on:blur={eventHandlers['on:blur']}
		on:change={eventHandlers['on:change']}
		on:click={eventHandlers['on:click']}
	/>

	{#if showTextField === true}
		<Textarea
			disabled={properties.disabled}
			bind:value={additionalInput}
			on:blur={additionalEventHandlers['on:blur']}
			on:change={additionalEventHandlers['on:change']}
			on:click={additionalEventHandlers['on:click']}
		/>
	{/if}
</div>
