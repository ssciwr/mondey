<script lang='ts'>
import { goto } from "$app/navigation";
import { i18n } from "$lib/i18n.svelte";
import { Button, Card } from "flowbite-svelte";
</script>

<div class="flex justify-center px-4 mt-6">
<Card class="flex justify-center text-center max-w-prose bg-additional-color-400 min-w-full">
  <h5 class="mb-2 mt-4 text-xl font-bold text-gray-700 dark:text-white tracking-wide">{i18n.tr.frontpage.heading}</h5>
  <p class="mb-5 text-base text-gray-600 sm:text-md dark:text-gray-400">{i18n.tr.frontpage.summary}</p>
  <div class="justify-center mb-1 items-center mt-2">


      <Button class="text-bold text-md w-44 mb-2 m-1 dark:bg-gray-100 hover:bg-gray-600 dark:hover:bg-gray-600 hover:text-white bg-white text-gray-700" onclick ={() => {
        goto("/signup");
      }}>{i18n.tr.frontpage.buttonLabel}</Button>

      <Button class="text-bold text-md w-44 m-1 dark:text-white transition-colors hover:bg-gray-600 dark:hover:bg-gray-600 hover:text-white  max-lg:hover:bg-primary-800  bg-primary-600 text-white" onclick ={() => {
        goto("/userLand/userLogin");
        }}>
          {i18n.tr.login.profileButtonLabelDefault}
      </Button>
    </div>
</Card>
</div>
