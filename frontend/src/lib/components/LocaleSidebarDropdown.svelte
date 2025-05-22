<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { SidebarDropdownWrapper, SidebarItem } from "flowbite-svelte";
import { LanguageOutline } from "flowbite-svelte-icons";

let isOpen = $state(false);

function toggleIsOpen() {
	isOpen = !isOpen;
}
</script>

<SidebarDropdownWrapper {isOpen} label={i18n.locale} onclick={toggleIsOpen}>
    <svelte:fragment slot="icon">
        <LanguageOutline size="lg"/>
    </svelte:fragment>
    {#each i18n.locales as locale}
        <SidebarItem label={locale} onclick={() => {isOpen = false; i18n.locale = locale;}}/>
    {/each}
</SidebarDropdownWrapper>
