<script lang='ts'>
import { goto } from "$app/navigation";
import { i18n } from "$lib/i18n.svelte";
import {  Card, Tooltip } from "flowbite-svelte";
</script>

<div class="flex justify-center px-4 mt-6">
<Card class="flex justify-center text-center max-w-prose bg-additional-color-200 min-w-full">
  <h1 class="h1">{i18n.tr.frontpage.heading}</h1>
  <p class="text-muted">{i18n.tr.frontpage.summary}</p>
  <div class="justify-center mb-1 items-center mt-2">

      <button class="btn-primary" onclick ={() => {
        goto("/signup");
      }}>{i18n.tr.frontpage.buttonLabel}</button>
      <Tooltip>{i18n.tr.frontpage.toolTip}</Tooltip>
  </div>
</Card>
</div>
