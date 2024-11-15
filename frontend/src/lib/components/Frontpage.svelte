<svelte:options runes={true} />
<script lang='ts'>
import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";
import FrontPageAbout from "$lib/components/FrontPageAbout.svelte";

let { items = [] } = $props();
</script>

<FrontPageCard
/>

<FrontPageAbout
/>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
/>
