<svelte:options runes={true} />

<script lang="ts">
import { preventDefault } from "$lib/util";
import { TrashBinOutline } from "flowbite-svelte-icons";
import Button from "flowbite-svelte/Button.svelte";

let {
	filename,
	ondelete,
}: { filename: string; ondelete: (event: Event) => void } = $props();
</script>

<div class="flex flex-col m-2 justify-center">
<img
        src={`${import.meta.env.VITE_MONDEY_API_URL}/static/${filename}`}
        width="96"
        height="96"
        alt={`${filename}`}

/>
<Button color="red" onclick={preventDefault(ondelete)} class="w-24 rounded-none mt-1"><TrashBinOutline class="h-5 w-5" /></Button>
</div>
