<svelte:options runes={true} />

<script lang="ts">
import CloseOutline from "flowbite-svelte-icons/CloseOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";
import { _ } from "svelte-i18n";

let {
	onclick = () => {
		console.log("empty onclick");
	},
}: { onclick?: () => void } = $props();
</script>

<Button color="alternative" {onclick}
	><CloseOutline class="me-2 h-5 w-5" /> {$_('admin.cancel')}</Button
>
