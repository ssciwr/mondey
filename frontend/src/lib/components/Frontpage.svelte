<svelte:options runes={true} />
<script lang='ts'>
import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";

let { items = [] } = $props();
</script>

<FrontPageCard
/>

<FrontPageAbout
/>

<div class="flex mt-7 flex-col text-center justify-center items-center space-y-6">
  <h1 class="text-2xl dark:text-white justify-center text-center text-balance max-w-prose font-bold text-gray-700">{$_('frontpageBookmarks.title')}</h1>
   <FrontPageBookmarks {bookmarks} />
  </div>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
/>
