<svelte:options runes={true} />

<script lang="ts">
	import Button from 'flowbite-svelte/Button.svelte';
	import CheckOutline from 'flowbite-svelte-icons/CheckOutline.svelte';
	import { _ } from 'svelte-i18n';

	let { onclick }: { onclick: () => void } = $props();
</script>

<Button color="green" {onclick}
	><CheckOutline class="me-2 h-5 w-5" /> {$_('admin.save-changes')}</Button
>
