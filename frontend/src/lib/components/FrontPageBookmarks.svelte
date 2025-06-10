<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte.js";
import BrainOutline from "flowbite-svelte-icons/BrainOutline.svelte";
import GraduationCapOutline from "flowbite-svelte-icons/GraduationCapOutline.svelte";
import HeartOutline from "flowbite-svelte-icons/HeartOutline.svelte";
import LanguageOutline from "flowbite-svelte-icons/LanguageOutline.svelte";
import PenOutline from "flowbite-svelte-icons/PenOutline.svelte";
import RocketOutline from "flowbite-svelte-icons/RocketOutline.svelte";
import UsersGroupOutline from "flowbite-svelte-icons/UsersGroupOutline.svelte";

const bookmarks = [
	{
		key: "Motor",
		icon: RocketOutline,
		emoji: "🏃",
	},
	{
		key: "FineMotor",
		icon: PenOutline,
	},
	{
		key: "Thinking",
		icon: BrainOutline,
	},
	{
		key: "Language",
		icon: LanguageOutline,
	},
	{
		key: "SocialDevelopment",
		icon: UsersGroupOutline,
	},
	{
		key: "InnerStates",
		icon: HeartOutline,
	},
	{
		key: "School",
		icon: GraduationCapOutline,
	},
];

let activeIndex = $state(0);

function selectTab(index: number) {
	activeIndex = activeIndex === index ? -1 : index; // Toggle accordion
}
</script>

<div class="w-full px-4 mx-auto">
    <div class="max-w-2xl mx-auto space-y-2">
        {#each bookmarks as { key, icon, emoji }, index}
            <div class="w-full">
                <button
                        class={activeIndex === index
                            ? "w-full text-left p-4 rounded-lg border dark:border-primary-700 border-primary-300 bg-primary-500 dark:bg-primary-900 transition-all duration-200"
                            : "w-full text-left p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-primary-500 hover:text-white dark:hover:bg-gray-750 transition-all duration-200"
                        }
                        onclick={() => selectTab(index)}
                >
                    <div class="flex items-center gap-3">
                        <div class="flex-shrink-0 p-2 rounded-lg bg-gray-100 dark:bg-gray-700">
                            {#if emoji}
                                <span class="text-2xl emoji-solid-gray">{emoji}</span>
                            {:else}
                                <svelte:component this={icon} size="md" color="#6b7280" />
                            {/if}
                        </div>
                        <div class="flex-1">
                            <h3 class="font-medium hover:text-white {activeIndex === index ? 'text-white' : ' hover:text-white dark:text-white'}">
                                {i18n.tr.frontpageBookmarks?.[`heading${key}`]}
                            </h3>
                        </div>
                        <div class="flex-shrink-0 transform transition-transform duration-200 {activeIndex === index ? 'rotate-180' : ''}">
                            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </div>
                    </div>
                </button>
                {#if activeIndex === index}
                    <div class="mt-2 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 text-left">
                        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
                            {i18n.tr.frontpageBookmarks?.[`summary${key}`]}
                        </p>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    .emoji-solid-gray {
        color: transparent;
        text-shadow: 0 0 0 rgb(145,145,155);
        opacity:0.8;
        font-size:1em;
    }
</style>
