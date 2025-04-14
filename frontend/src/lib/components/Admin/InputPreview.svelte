<svelte:options runes={true} />

<script lang="ts">
import type { UserQuestionAdmin } from "$lib/client/types.gen";
import { Input, Label, Select, type SelectOptionType } from "flowbite-svelte";
let {
	data,
	lang,
	answer = $bindable(),
}: { data: UserQuestionAdmin; lang: string; answer: string } = $props();
let items: Array<SelectOptionType<string>> = $derived(parse_options_json());
let selected_answer = $state("");
let additional_answer = $state("");
let free_text = $derived(
	data.additional_option && data.additional_option === selected_answer,
);
$effect(() => {
	answer = free_text ? additional_answer : selected_answer;
});

function parse_options_json() {
	try {
		const options_json = data.text[lang].options_json;
		return JSON.parse(options_json);
	} catch (e) {
		console.log("Couldn't parse options_json");
		console.log(e);
	}
	return [];
}
</script>

<div class="mb-5">
	<Label class="font-semibold text-gray-700 dark:text-gray-400">{data.text[lang].question}</Label>
</div>
<div class="mb-5">
	{#if data.component === 'select'}
		<Select {items} bind:value={selected_answer} placeholder="" />
		{#if free_text}
			<Input type="text" bind:value={additional_answer} />
		{/if}
	{:else}
		<Input type="text" bind:value={selected_answer} />
	{/if}
</div>
