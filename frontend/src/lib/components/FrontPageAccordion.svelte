<script>
    import { AccordionItem, Accordion } from 'flowbite-svelte';
    import { _ } from 'svelte-i18n';
 
    const parseMarkdown = (markdown) => {
    if (!markdown) return markdown;
 
    return markdown
      .replace(/###\s(.+)/g, '<h3>$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
      .replace(/__(.+?)__/g, '<u>$1</u>')
      .replace(/\n/g, '<br>')
      .replace(/(?:^|\n)[*-]\s(.+)/g, '<li>$1</li>');
  };
 
  </script>
   <Accordion class="min-w-full px-4 mt-10">
        <AccordionItem class="bg-additional-color-400 hover:bg-additional-color-50 hover:text-gray-700 text-gray-700 pl-14">
        <span slot="header">{$_('frontpageAccordion.heading1')}</span>
      <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400">{@html parseMarkdown($_('frontpageAccordion.summary1'))}</p>
    </AccordionItem>
 
    <AccordionItem class="bg-additional-color-200 hover:bg-additional-color-50 text-gray-700 pl-14">
        <span slot="header">{$_('frontpageAccordion.heading2')}</span>
        <p class="mb-4 mt-4 px-4 text-gray-700 dark:text-gray-400">{$_('frontpageAccordion.summary2')}</p>
      </AccordionItem>
  </Accordion>
 