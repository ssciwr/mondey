<script>
 import { List, DescriptionList, Heading, P } from "flowbite-svelte";
</script>

<Heading tag="h3" class="divide-y divide-gray-200 text-gray-900 dark:divide-gray-700 dark:text-white pt-12 pb-2 pl-12">Kontaktieren Sie uns!</Heading>
<P class="divide-y divide-gray-200 text-gray-500 dark:divide-gray-700 dark:text-white pl-12 pb-12">Wir freuen uns über Ihre Rückmeldungen und sind dankbar für Anregungen zur Verbesserung unserer Webseite.</P>

<List tag="dl" class="divide-y divide-gray-200 text-gray-900 dark:divide-gray-700 dark:text-white pl-12">
     <div class="flex flex-col pb-5">
       <DescriptionList tag="dt" class="mb-1">Projektleiterin</DescriptionList>
       <DescriptionList tag="dd" class="text-md">Prof. Dr. Sabina Pauen</DescriptionList>
   </div>
   <div class="flex flex-col pb-5">
       <DescriptionList tag="dt" class="mb-1">Anschrift</DescriptionList>
       <DescriptionList tag="dd" class="text-md">Psychologisches Institut Universität Heidelberg</DescriptionList>
       <DescriptionList tag="dd" class="text-md">Hauptstraße 47-51 69117 Heidelberg</DescriptionList>
   </div>
       <div class="flex flex-col pb-5">
       <DescriptionList tag="dt" class="mb-1">Unsere E-Mail</DescriptionList>
       <DescriptionList tag="dd" class="text-md">support@psychologie.uni-heidelberg.de</DescriptionList>
   </div>
   <div class="flex flex-col pb-5">
       <DescriptionList tag="dt" class="mb-1">Unsere Telefonnummer</DescriptionList>
       <DescriptionList tag="dd" class="text-md">+49 6221 547346</DescriptionList>
   </div>
</List>