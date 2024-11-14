<script>
// @ts-nocheck
import { base } from "$app/paths";

import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
import Card from "$lib/components/Card.svelte";
import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";

export let getStarted = "";

export let items = [];

const props = {};
</script>

<Card
/>

<GalleryDisplay
	withSearch={false}
	itemComponent={CardDisplay}
	data={items}
	componentProps={props}
/>
