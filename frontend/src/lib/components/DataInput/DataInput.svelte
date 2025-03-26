<svelte:options runes={true} />

<script lang="ts">
import { Label, Textarea } from "flowbite-svelte";

// variables
let {
	component = null,
	value = $bindable(null),
	additionalValue = $bindable(null),
	label = null,
	componentClass = "",
	textTrigger = "",
	required = false,
	disabled = false,
	additionalRequired = false,
	id = undefined,
	items = [],
	placeholder = undefined,
	kwargs = {},
}: {
	component?: any;
	value?: any;
	additionalRequired?: boolean;
	label?: string | null;
	componentClass?: string;
	textTrigger?: string;
	additionalValue?: any;
	required?: boolean;
	disabled?: boolean;
	id?: string | undefined;
	items?: any[];
	placeholder?: string | undefined;
	kwargs?: any;
} = $props();

// functionality for showing the textfield when the trigger is selected
function checkShowTextfield(v: any): boolean {
	let basic =
		value !== undefined &&
		value !== null &&
		value !== "" &&
		textTrigger !== undefined &&
		textTrigger !== null &&
		textTrigger !== "";
	if (Array.isArray(v)) {
		return v.includes(textTrigger) && basic;
	}
	return v === textTrigger && basic;
}

let valid: boolean = $state(false);
let showTextField: boolean = $state(false);
let highlight = $state(false);
$effect(() => {
	highlight = !valid && required === true;
});
$effect(() => {
	showTextField = checkShowTextfield(value);
});
</script>

{#if label}
	<Label for={id} class="font-semibold text-gray-700 dark:text-gray-400"
		>{label}
		{#if required && false === disabled}
			&nbsp;*
		{/if}
	</Label
	>
{/if}

<div class="space-y-4">
	<svelte:component
		this={component}
		class={highlight
			? "rounded border-2 border-primary-600 dark:border-primary-600 " +
				componentClass
			: componentClass}
		bind:value = {value}
		{placeholder}
		{items}
		{required}
		{disabled}
		{...kwargs}
	/>

	{#if showTextField === true}
		<Textarea
			bind:value={additionalValue}
			required={additionalRequired}
			{disabled}
		/>
	{/if}
</div>
