<script>
// @ts-nocheck
import { base } from "$app/paths";

import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
import FrontPageCard from "$lib/components/FrontPageCard.svelte";

export let getStarted = "";

export let items = [];

const props = {};
</script>

<FrontPageCard
/>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
	componentProps={props}
/>
