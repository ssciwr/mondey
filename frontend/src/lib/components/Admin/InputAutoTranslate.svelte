<svelte:options runes={true}/>

<script lang="ts">
import { translate } from "$lib/client";
import {
	Button,
	ButtonGroup,
	Input,
	InputAddon,
	Spinner,
	Textarea,
} from "flowbite-svelte";
import { WandMagicSparklesOutline } from "flowbite-svelte-icons";

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

let translate_button_disabled = $state(false);

async function getTranslation() {
	translate_button_disabled = true;
	const { data, error } = await translate({
		query: { locale: locale, text: de_text },
	});
	if (error || !data) {
		console.log(error);
	} else {
		value = data;
	}
	translate_button_disabled = false;
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
        <Button disabled={translate_button_disabled} onclick={getTranslation}>
            {#if translate_button_disabled}
                <Spinner class="h-5 w-5"/>
            {:else}
                <WandMagicSparklesOutline class="h-5 w-5"/>
            {/if}
        </Button>
    {/if}
</ButtonGroup>
