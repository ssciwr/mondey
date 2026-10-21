<script lang="ts">
import { DarkMode } from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
import FunctionalIcon from "#lib/components/Navigation/FunctionalIcon.svelte";
import { i18n } from "#lib/i18n.svelte.ts";
</script>

<FunctionalIcon tooltip={i18n.tr.frontpage.toggleDarkmode}>
    <DarkMode class="rounded-lg p-2 text-xl text-gray-500 dark:text-gray-500 hover:text-primary-800 dark:hover:text-primary-800">
        {#snippet darkIcon()}
            <MoonSolid />
        {/snippet}
        {#snippet lightIcon()}
            <SunSolid />
        {/snippet}
    </DarkMode>
</FunctionalIcon>
