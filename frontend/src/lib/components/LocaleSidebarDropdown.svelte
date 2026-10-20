<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { SidebarDropdownWrapper, SidebarItem } from "flowbite-svelte";
import { LanguageOutline } from "flowbite-svelte-icons";

let isOpen = $state(false);
</script>

<SidebarDropdownWrapper bind:isOpen label={i18n.locale}>
    {#snippet icon()}
        <LanguageOutline size="lg"/>
    {/snippet}
    {#each i18n.locales as locale}
        <SidebarItem label={locale} aClass="cursor-pointer" onclick={() => {isOpen = false; i18n.locale = locale;}}/>
    {/each}
</SidebarDropdownWrapper>
