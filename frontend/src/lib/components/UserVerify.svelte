<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Button } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
</script>

<div
	class="m-2 mx-auto flex w-full items-center justify-center p-2 text-gray-700 dark:text-gray-400"
>
	<CheckCircleOutline size="xl" color="green" class="m-2" />
	<div class="m-2 p-2">
		{i18n.tr.registration.successMessage}
	</div>
</div>
<Button
	type="button"
	class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
	href="/"
>
	{i18n.tr.registration.goHome}
</Button>
