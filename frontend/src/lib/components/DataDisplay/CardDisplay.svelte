<svelte:options runes={true}/>
<script lang="ts">
import { isDark } from "$lib/components/DataDisplay/color_utils";
import { Card } from "flowbite-svelte";
import type { Snippet } from "svelte";

let {
	title = "",
	text = "",
	image = "",
	color = undefined,
	cardClasses = "",
	titleClasses = "",
	disabled = false,
	onclick,
	children,
}: {
	title?: string;
	text?: string;
	image?: string;
	color?: string;
	onclick: () => void;
	cardClasses?: string;
	titleClasses?: string;
	disabled?: boolean;
	children?: Snippet;
} = $props();

let textColor = $derived(isDark(color) ? "text-white" : "text-black");
</script>

<Card
        class={`${disabled ? 'opacity-30' : 'cursor-pointer hover:scale-105 hover:transition-color hover:cursor-pointer'} flex flex-col h-full mr-2 max-w-prose ${cardClasses}`}
        style={color ? `background-color: ${color}` : ""}
        horizontal={false}
        img={image}
        imgClass="max-md:hidden object-scale-down"
        on:click={!disabled ? onclick : () => {}}
>
        {#if title}
            <div>
                <h5 class={`break-words hyphens-auto mb-2 text-xl font-bold tracking-tight ${color ? textColor : ''} ${titleClasses}`}>
                    {title}
                </h5>
            </div>
        {/if}

        <div class="flex-grow mb-2">
            {#if text}
                <p class={`font-normal leading-tight opacity-60 ${color ? textColor : ''}`}>
                    {text}
                </p>
            {/if}
        </div>

        <div class={`mt-auto pt-4 flex flex-col ${color ? textColor : ''}`}>
            {#if !disabled}
                {@render children?.()}
            {/if}
        </div>
</Card>
