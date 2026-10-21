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
	color?: string | null;
	onclick: () => void;
	cardClasses?: string;
	titleClasses?: string;
	disabled?: boolean;
	children?: Snippet;
} = $props();

let textColor = $derived(isDark(color) ? "text-white" : "text-black");
</script>

<Card
        class={`${disabled ? 'opacity-30' : 'cursor-pointer hover:scale-105 hover:transition-color hover:cursor-pointer'} flex flex-col h-full mr-2 max-w-prose p-0 sm:p-0 ${cardClasses}`}
        style={color ? `background-color: ${color}` : ""}
        horizontal={false}
        img={image}
        classes={{ image: "max-md:hidden w-full aspect-4/3 object-cover" }}
        onclick={!disabled ? onclick : () => {}}
>
        <!-- the content is padded rather than the card, so that an image fills the top of the card -->
        <div class="flex flex-col grow p-4 sm:p-6">
            {#if title}
                <div>
                    <h5 class={`wrap-break-word hyphens-auto mb-2 text-xl font-bold tracking-tight ${color ? textColor : ''} ${titleClasses}`}>
                        {title}
                    </h5>
                </div>
            {/if}

            <div class="grow mb-2">
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
        </div>
</Card>
