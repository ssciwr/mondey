<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import CloseOutline from "flowbite-svelte-icons/CloseOutline.svelte";
import Button from "flowbite-svelte/Button.svelte";

let {
	onclick = () => {
		console.log("empty onclick");
	},
}: { onclick?: () => void } = $props();
</script>

<Button color="alternative" {onclick} data-testid="cancelButton">
	<CloseOutline class="me-2 h-5 w-5" /> {i18n.tr.admin.cancel}
</Button>
