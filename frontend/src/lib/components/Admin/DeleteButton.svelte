<svelte:options runes={true} />

<script lang="ts">
	import Button from 'flowbite-svelte/Button.svelte';
	import TrashBinOutline from 'flowbite-svelte-icons/TrashBinOutline.svelte';
	import { _ } from 'svelte-i18n';

	let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button color="red" {onclick}><TrashBinOutline class="me-2 h-5 w-5" /> {$_('admin.delete')}</Button>
