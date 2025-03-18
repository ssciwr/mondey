<script>
import { i18n } from "$lib/i18n.svelte";
import { Accordion, AccordionItem } from "flowbite-svelte";
</script>

   <Accordion class="min-w-full px-4 mt-10">
        <AccordionItem >
        <span slot="header">{i18n.tr.frontpageAccordion.heading1}</span>
      <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400">{@html i18n.tr.frontpageAccordion.summary1}</p>
    </AccordionItem>

    <AccordionItem>
        <span slot="header">{i18n.tr.frontpageAccordion.heading2}</span>
        <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400">{@html i18n.tr.frontpageAccordion.summary2}</p>
      </AccordionItem>
  </Accordion>
