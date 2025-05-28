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

const styleTemplate = {
	buttonClass:
		"w-full text-left p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-primary-500 dark:hover:bg-gray-750 transition-all duration-200",
	activeButtonClass:
		"w-full text-left p-4 rounded-lg border dark:border-primary-700 border-primary-300 bg-primary-500 dark:bg-primary-900 transition-all duration-200",
	contentClass:
		"mt-2 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 text-left",
	iconBgClass: "p-2 rounded-lg bg-gray-100 dark:bg-gray-700",
	iconColor: "#6b7280", // gray-500
};

const bookmarks = [
	{
		titleKey: i18n.tr.frontpageBookmarks.headingMotor,
		contentKey: i18n.tr.frontpageBookmarks.summaryMotor,
		icon: RocketOutline,
		emoji: "🏃",
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingFineMotor,
		contentKey: i18n.tr.frontpageBookmarks.summaryFineMotor,
		icon: PenOutline,
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingThinking,
		contentKey: i18n.tr.frontpageBookmarks.summaryThinking,
		icon: BrainOutline,
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingLanguage,
		contentKey: i18n.tr.frontpageBookmarks.summaryLanguage,
		icon: LanguageOutline,
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingSocialDevelopment,
		contentKey: i18n.tr.frontpageBookmarks.summarySocialDevelopment,
		icon: UsersGroupOutline,
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingInnerStates,
		contentKey: i18n.tr.frontpageBookmarks.summaryInnerStates,
		icon: HeartOutline,
		...styleTemplate,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingSchool,
		contentKey: i18n.tr.frontpageBookmarks.summarySchool,
		icon: GraduationCapOutline,
		...styleTemplate,
	},
];

let activeIndex = $state(0);

function selectTab(index: number) {
	activeIndex = activeIndex === index ? -1 : index; // Toggle accordion
}
</script>

<div class="w-full px-4 mx-auto">
    <div class="max-w-2xl mx-auto space-y-2">
        {#each bookmarks as { titleKey, contentKey, icon, emoji, buttonClass, activeButtonClass, contentClass, iconBgClass, iconColor }, index}
            <div class="w-full">
                <button
                        class={activeIndex === index ? activeButtonClass : buttonClass}
                        onclick={() => selectTab(index)}
                >
                    <div class="flex items-center gap-3">
                        <div class="flex-shrink-0 {iconBgClass}">
                            {#if emoji}
                                <span class="text-2xl emoji-solid-gray">{emoji}</span>
                            {:else}
                                <svelte:component this={icon} size="md" color={iconColor} />
                            {/if}
                        </div>
                        <div class="flex-1">
                            <h3 class="font-medium hover:text-white {activeIndex === index ? 'text-white' : 'text-gray-900 dark:text-white'}">
                                {titleKey}
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
                    <div class={contentClass}>
                        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
                            {contentKey}
                        </p>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    .emoji-gray {
        filter: grayscale(100%);
        opacity:0.8;
        font-size:1em;
    }
    .emoji-solid-gray {
        color: transparent;
        text-shadow: 0 0 0 rgb(145,145,155);
        opacity:0.8;
        font-size:1em;
    }
</style>
