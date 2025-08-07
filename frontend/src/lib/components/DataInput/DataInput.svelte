<svelte:options runes={true} />

<script lang="ts">
import Fileupload from "$lib/components/DataInput/Fileupload.svelte";
import { i18n } from "$lib/i18n.svelte";
import {
	Input,
	Label,
	Select,
	type SelectOptionType,
	Textarea,
} from "flowbite-svelte";
export type Component = "input" | "textarea" | "select" | "fileupload";

const componentTable = {
	input: Input,
	textarea: Textarea,
	select: Select,
	fileupload: Fileupload,
};

// variables
let {
	component = "input",
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
	testid = undefined,
}: {
	component?: Component;
	value?: any;
	additionalRequired?: boolean;
	label?: string | null;
	componentClass?: string;
	textTrigger?: string;
	additionalValue?: any;
	required?: boolean;
	disabled?: boolean;
	id?: string | undefined;
	items?: SelectOptionType<string | number>[];
	placeholder?: string | undefined;
	kwargs?: any;
	testid?: string;
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
let derivedPlaceholder = $derived(
	placeholder ??
		(component === "select" ? i18n.tr.misc.selectPlaceholder : undefined),
);
</script>

{#if label}
	<Label
			for={id}
			class="font-semibold text-gray-700 dark:text-gray-400 {required && false === disabled ? 'border-l-2 border-additional-color-300 dark:border-additional-color-600 pl-2' : ''}"
	>
		{label}
		{#if required && false === disabled}
			&nbsp;* {i18n.tr.misc.selectPlaceholder}
		{/if}
	</Label>
{/if}

<div class="space-y-4">
	<svelte:component
		this={componentTable[component]}
		class={highlight
			? "rounded border-2 border-primary-600 dark:border-primary-600 " +
				componentClass
			: componentClass}
		bind:value = {value}
		placeholder = {derivedPlaceholder}
		{items}
		{required}
		{disabled}
		{...kwargs}
		for={label}
		data-testid={testid}
	/>

	{#if showTextField === true}
		<Textarea
			bind:value={additionalValue}
			required={additionalRequired}
			{disabled}
		/>
	{/if}
</div>
