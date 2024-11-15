<svelte:options runes={true} />
<script lang='ts'>
import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";

let { items = [] } = $props();
</script>

<FrontPageCard
/>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
/>
