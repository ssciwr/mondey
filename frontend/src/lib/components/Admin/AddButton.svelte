<svelte:options runes={true} />

<script lang="ts">
	import Button from 'flowbite-svelte/Button.svelte';
	import PlusOutline from 'flowbite-svelte-icons/PlusOutline.svelte';
	import { _ } from 'svelte-i18n';

	let { onclick, disabled = false }: { onclick: () => void; disabled?: boolean } = $props();
</script>

<Button color="blue" {onclick} {disabled}
	><PlusOutline class="me-2 h-5 w-5" /> {$_('admin.add')}</Button
>
