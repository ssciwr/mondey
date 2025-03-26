<svelte:options runes={true} />

<script lang="ts">
import { translate } from "$lib/client";
import { i18n } from "$lib/i18n.svelte";
import { ButtonGroup, Input, InputAddon, Textarea } from "flowbite-svelte";
import WandMagicSparklesOutline from "flowbite-svelte-icons/WandMagicSparklesOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let {
	value = $bindable(""),
	locale,
	de_text,
	placeholder = "",
	multiline = false,
}: {
	value: string;
	locale: string;
	de_text: string;
	placeholder?: string;
	multiline?: boolean;
} = $props();

async function getTranslation(text: string, locale: string): Promise<string> {
	const { data, error } = await translate({
		query: { locale: locale, text: text },
	});
	if (error) {
		console.log(error);
		return "";
	}
	return data;
}
</script>

<ButtonGroup class="w-full">
<InputAddon>{locale}</InputAddon>
	{#if multiline}
		<Textarea bind:value={value} placeholder={placeholder}/>
		{:else}
<Input bind:value={value} placeholder={placeholder}/>
		{/if}
{#if locale !== "de"}
	<Button onclick={async () => {value = await getTranslation(de_text, locale)}}>
		<WandMagicSparklesOutline class="h-5 w-5" />
	</Button>
{/if}
</ButtonGroup>
