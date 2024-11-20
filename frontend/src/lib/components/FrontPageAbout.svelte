<script>
import babyFlower from "$lib/assets/babyFlower.jpg";
import { Card } from "flowbite-svelte";
import { _ } from "svelte-i18n";
</script>

  <div class="flex mt-6 justify-center min-w-full">
    <Card horizontal class="max-w-4xl shadow-none border-none flex items-start space-x-6">
      <img src={babyFlower} alt="{$_("frontpageAbout.alt")}" class="rounded-lg min-[768px]:w-1/3 max-[768px]:aspect-[16/8] max-[768px]:object-cover">
      <div class="flex items-start flex-col">
      <h5 class="mb-8 mt-5 text-2xl font-bold tracking-tight text-gray-700 dark:text-white">{$_("frontpageAbout.heading")}</h5>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{$_("frontpageAbout.summary1")}</p>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{$_("frontpageAbout.summary2")}</p>
      </div>
    </Card>
  </div>
