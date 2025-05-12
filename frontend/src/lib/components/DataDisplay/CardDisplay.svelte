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
	children?: Snippet;
} = $props();

let textColor = $derived(isDark(color) ? "text-white" : "text-black");
</script>

<Card
        class={`hover:transition-color flex flex-col h-full cursor-pointer hover:scale-105 child-card hover:cursor-pointer mr-2 max-w-prose ${cardClasses}`}
        style={color ? `background-color: ${color}` : "bg-primary dark:bg-primary hover:bg-additional-color-800 dark:hover:bg-additional-color-700"}
        horizontal={false}
        img={image}
        imgClass="max-md:hidden object-scale-down"
        on:click={onclick}
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
            {@render children?.()}
        </div>
</Card>
