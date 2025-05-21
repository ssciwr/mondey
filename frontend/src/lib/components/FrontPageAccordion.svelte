<script>
import { i18n } from "$lib/i18n.svelte";
import DOMPurify from "dompurify";
import { Accordion, AccordionItem } from "flowbite-svelte";

const sanitizeConfig = {
	ALLOWED_TAGS: ["strong", "p", "i", "ul", "li", "ol"],
	ALLOWED_ATTR: [], // explicitly none
};

function sanitizeHtml(html) {
	return DOMPurify.sanitize(html, sanitizeConfig);
}
</script>

<Accordion class="min-w-full px-4 mt-10">
    <AccordionItem>
        <span slot="header">{i18n.tr.frontpageAccordion.heading1}</span>
        <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400 whitespace-pre-line">
            {@html sanitizeHtml(i18n.tr.frontpageAccordion.summary1)}
        </p>
    </AccordionItem>

    <AccordionItem>
        <span slot="header">{i18n.tr.frontpageAccordion.heading2}</span>
        <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400 whitespace-pre-line">
            {@html sanitizeHtml(i18n.tr.frontpageAccordion.summary2)}
        </p>
    </AccordionItem>
</Accordion>
