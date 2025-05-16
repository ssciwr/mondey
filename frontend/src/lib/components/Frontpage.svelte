<svelte:options runes={true} />
<script lang='ts'>
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import { i18n } from "$lib/i18n.svelte";
import FrontPageAccordion from "./FrontPageAccordion.svelte";
import FrontPageBookmarks from "./FrontPageBookmarks.svelte";

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
</script>

<FrontPageCard/>

<FrontPageAbout/>

<div class="flex mt-7 flex-col text-center justify-center items-center space-y-6">
  <h1 class="text-2xl dark:text-white justify-center text-center text-balance max-w-prose font-bold text-gray-700">{i18n.tr.frontpageBookmarks.title}</h1>
  <FrontPageBookmarks {bookmarks} />
</div>

<FrontPageAccordion/>
