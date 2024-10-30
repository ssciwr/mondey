<script lang="ts">
	import { Button, ButtonGroup } from 'flowbite-svelte';

	export let buttons: unknown = [];
</script>

<ButtonGroup class="mt-6 flex justify-center">
	{#each buttons as bprops}
		<Button
			href={bprops.href}
			disabled={bprops.disabled}
			class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
			{...bprops.props}
			on:click={bprops.onclick}
			>{bprops.label}
		</Button>
	{/each}
</ButtonGroup>
