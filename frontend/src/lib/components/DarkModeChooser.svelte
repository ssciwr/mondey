<script>
import FunctionalIcon from "$lib/components/Navigation/FunctionalIcon.svelte";
import { DarkMode } from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
import { i18n } from "$lib/i18n.svelte";
</script>

<FunctionalIcon tooltip={i18n.tr.frontpage.toggleDarkmode}>
    <DarkMode class="apply-icon-style">
        <MoonSolid slot="darkIcon" />
        <SunSolid slot="lightIcon" />
    </DarkMode>
</FunctionalIcon>
