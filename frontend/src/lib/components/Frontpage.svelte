<svelte:options runes={true} />
<script lang='ts'>
import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import FrontPageBookmarks from "./FrontPageBookmarks.svelte";
import { _ } from "svelte-i18n";

let { items = [] } = $props();

const bookmarks = [
  
   { titleKey: $_('frontpageBookmarks.headingMotor') , contentKey: $_('frontpageBookmarks.summaryMotor') },
   { titleKey: $_('frontpageBookmarks.headingFineMotor') , contentKey: $_('frontpageBookmarks.summaryFineMotor') },
   { titleKey: $_('frontpageBookmarks.headingThinking') , contentKey: $_('frontpageBookmarks.summaryThinking') },
   { titleKey: $_('frontpageBookmarks.headingLanguage') , contentKey: $_('frontpageBookmarks.summaryLanguage') },
   { titleKey: $_('frontpageBookmarks.headingSocialDevelopment') , contentKey: $_('frontpageBookmarks.summarySocialDevelopment') },
   { titleKey: $_('frontpageBookmarks.headingInnerStates') , contentKey: $_('frontpageBookmarks.summaryInnerStates') },
   { titleKey: $_('frontpageBookmarks.headingSchool') , contentKey: $_('frontpageBookmarks.summarySchool') },
   ];

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
