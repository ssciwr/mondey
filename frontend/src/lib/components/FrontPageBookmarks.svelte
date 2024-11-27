<script>
    export let bookmarks = [];
    import { _ } from "svelte-i18n";

    let activeIndex = 0;
    let interval;

    function changeTab() {
        activeIndex = (activeIndex + 1) % bookmarks.length;
    }

    import { onMount } from "svelte";
    onMount(() => {
        interval = setInterval(changeTab, 4000);

        return () => {
            clearInterval(interval);
        };
    });

    function selectTab(index) {
        activeIndex = index;
        clearInterval(interval);
    }
  </script>

   <div class="w-full min-w-full px-4 mx-auto">
    <!-- Tabs (Bookmarks) -->
    <div class="flex max-lg:flex-col max-md:min-w-full lg:flex-row border-b justify-center items-center px-2">
      {#each bookmarks as { titleKey }, index}
        <button
          class="flex-1 rounded-lg text-base text-center lg:min-h-fit max-lg:min-w-80 py-2 px-4 dark:text-white text-gray-600 transition-colors hover:text-grey-900 max-lg:hover:bg-primary-800 dark:hover:text-gray-900 hover:bg-additional-color"
          class:bg-primary-600={activeIndex === index}
          class:text-white={activeIndex === index}
          on:click={() => selectTab(index)}
        >
          {titleKey}
        </button>
      {/each}
    </div>

     <div class="p-6 bg-gray-100 dark:bg-gray-800 text-center rounded-lg shadow-md mt-2 space-y-4">
      <p class="text-gray-700 dark:text-gray-400 text-balance mt-4 mb-4">
        {bookmarks[activeIndex]?.contentKey}</p>
    </div>

  </div>