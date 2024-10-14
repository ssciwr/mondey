<svelte:options runes={true} />

<script lang="ts">
	import Button from 'flowbite-svelte/Button.svelte';
	import EditOutline from 'flowbite-svelte-icons/EditOutline.svelte';
	import { _ } from 'svelte-i18n';

	let { onclick }: { onclick: (event: Event) => void } = $props();
</script>

<Button color="yellow" {onclick}><EditOutline class="me-2 h-5 w-5" /> {$_('admin.edit')}</Button>
