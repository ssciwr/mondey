<script>
import babyFlower from "$lib/assets/babyFlower.jpg";
import { Card } from "flowbite-svelte";
import { _ } from "svelte-i18n";
</script>

  <div class="flex mt-4 justify-center min-w-full">
    <Card img={babyFlower} horizontal size="full" class="shadow-none border-none">
      <h5 class="mb-8 mt-2 text-2xl font-bold tracking-tight text-gray-700 dark:text-white">{$_("frontpageAbout.heading")}</h5>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{$_("frontpageAbout.summary1")}</p>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{$_("frontpageAbout.summary2")}</p>
    </Card>
  </div>
