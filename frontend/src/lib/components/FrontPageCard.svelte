<script lang='ts'>
import { goto } from "$app/navigation";
import { Button, Card, Tooltip } from "flowbite-svelte";
import { _ } from "svelte-i18n";
</script>

<div class="flex justify-center px-4 mt-6">
<Card class="flex justify-center text-center max-w-prose bg-additional-color min-w-full">
  <h5 class="mb-2 mt-4 text-xl font-bold text-gray-700 dark:text-white tracking-wide">{$_("frontpage.heading")}</h5>
  <p class="mb-5 text-base text-gray-600 sm:text-md dark:text-gray-400">{$_("frontpage.summary")}</p>
  <div class="justify-center mb-1 items-center mt-2">
      <Button class="text-bold text-md w-44 hover:text-white dark:text-white bg-white text-gray-700" onclick ={() => {
        goto("/signup");
      }}>{$_("frontpage.buttonLabel")}</Button>
      <Tooltip>{$_("frontpage.toolTip")}</Tooltip>
  </div>
</Card>
</div>
