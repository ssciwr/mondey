<script lang='ts'>
import { Button, Card, Tooltip } from "flowbite-svelte";
import { _ } from "svelte-i18n";
</script>

<Card class="flex justify-center mr-4 text-center max-w-prose bg-additional-color min-w-full">
  <h5 class="mb-2 mt-4 text-2xl font-bold text-gray-700 dark:text-white tracking-wide">{$_("frontpage.heading")}</h5>
  <p class="mb-5 text-base text-gray-600 sm:text-lg dark:text-gray-400">{$_("frontpage.summary")}</p>
  <div class="justify-center mb-1 items-center mt-2">
      <Button class="text-bold text-md w-44 hover:text-white dark:text-white bg-white text-gray-700">{$_("frontpage.buttonLabel")}</Button>
      <Tooltip>{$_("frontpage.toolTip")}</Tooltip>
  </div>
</Card>
