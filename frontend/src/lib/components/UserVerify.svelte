<script lang="ts">
	import { Button } from 'flowbite-svelte';
	import { CheckCircleOutline } from 'flowbite-svelte-icons';
	import { _ } from 'svelte-i18n';
</script>

<div
	class="m-2 mx-auto flex w-full items-center justify-center p-2 text-gray-700 dark:text-gray-400"
>
	<CheckCircleOutline size="xl" color="green" class="m-2" />
	<div class="m-2 p-2">
		{$_('registration.successMessage')}
	</div>
</div>
<Button
	type="button"
	class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
	href="/"
>
	{$_('registration.goHome')}
</Button>
