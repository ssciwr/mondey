<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte.js";
import { onMount } from "svelte";

const bookmarks = [
	{
		titleKey: i18n.tr.frontpageBookmarks.headingMotor,
		contentKey: i18n.tr.frontpageBookmarks.summaryMotor,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingFineMotor,
		contentKey: i18n.tr.frontpageBookmarks.summaryFineMotor,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingThinking,
		contentKey: i18n.tr.frontpageBookmarks.summaryThinking,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingLanguage,
		contentKey: i18n.tr.frontpageBookmarks.summaryLanguage,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingSocialDevelopment,
		contentKey: i18n.tr.frontpageBookmarks.summarySocialDevelopment,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingInnerStates,
		contentKey: i18n.tr.frontpageBookmarks.summaryInnerStates,
	},
	{
		titleKey: i18n.tr.frontpageBookmarks.headingSchool,
		contentKey: i18n.tr.frontpageBookmarks.summarySchool,
	},
];

let activeIndex = $state(0);
let interval: ReturnType<typeof setInterval>;

function changeTab() {
	activeIndex = (activeIndex + 1) % bookmarks.length;
}

onMount(() => {
	interval = setInterval(changeTab, 4000);

	return () => {
		clearInterval(interval);
	};
});

function selectTab(index: number) {
	activeIndex = index;
	clearInterval(interval);
}
</script>

   <div class="w-full min-w-full px-4 mx-auto">
    <!-- Tabs (Bookmarks) -->
    <div class="flex max-lg:flex-col max-md:min-w-full lg:flex-row border-b justify-center items-center px-2">
      {#each bookmarks as { titleKey }, index}
        <button
          class="flex-1 rounded-lg text-base text-center lg:min-h-fit max-lg:hover:text-white max-md:hover:text-white h-16 max-lg:min-w-80 py-2 px-4 dark:text-white hover:dark:text-white text-gray-600 transition-colors hover:text-gray-900 max-lg:hover:bg-primary-800 dark:hover:text-gray-900 hover:bg-gray-100 hover:dark:bg-gray-800"
          class:bg-primary-600={activeIndex === index}
          class:text-white={activeIndex === index}
          onclick={() => selectTab(index)}
        >
          {titleKey}
        </button>
      {/each}
    </div>

     <div class="p-6 px-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-md mt-2 space-y-4">
      <p class="flex text-left lg:ml-30 md:ml-10 ml-5 mr-7 text-gray-700 dark:text-gray-400 mt-4 mb-4">
        {bookmarks[activeIndex]?.contentKey}</p>
    </div>

  </div>
