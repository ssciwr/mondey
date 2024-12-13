<script>
import babyFlower from "$lib/assets/babyFlower.jpg";
import { i18n } from "$lib/i18n.svelte";
import { Card } from "flowbite-svelte";
</script>

  <div class="flex mt-6 justify-center min-w-full">
    <Card horizontal class="max-w-4xl shadow-none border-none flex items-start space-x-6">
      <img src={babyFlower} alt="{i18n.tr.frontpageAbout.alt}" class="rounded-lg md:w-1/3 max-md:aspect-[16/8] max-md:object-cover">
      <div class="flex items-start flex-col">
      <h5 class="mb-8 mt-5 text-2xl font-bold tracking-tight text-gray-700 dark:text-white">{i18n.tr.frontpageAbout.heading}</h5>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{i18n.tr.frontpageAbout.summary1}</p>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{i18n.tr.frontpageAbout.summary2}</p>
      </div>
    </Card>
  </div>
