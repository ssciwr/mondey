<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
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

let valid: boolean = $state(false);
let showTextField: boolean = $derived.by(
	// functionality for showing the textfield when the trigger is selected
	() => {
		let basic =
			value !== undefined &&
			value !== null &&
			value !== "" &&
			textTrigger !== undefined &&
			textTrigger !== null &&
			textTrigger !== "";
		if (!basic) {
			return false;
		}
		if (Array.isArray(value)) {
			return value.includes(textTrigger);
		}
		return value === textTrigger;
	},
);
let highlight = $derived(!valid && required === true);

let realPlaceholder = $derived(
	i18n.tr ? i18n.tr.misc.selectPlaceholder : undefined,
);
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
		{realPlaceholder}
		{items}
		{required}
		{disabled}
		{...kwargs}
		for={label}
	/>

	{#if showTextField === true}
		<Textarea

			bind:value={additionalValue}
			required={additionalRequired}
			{disabled}
		/>
	{/if}
</div>
