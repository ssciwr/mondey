<script>
import FunctionalIcon from "$lib/components/Navigation/FunctionalIcon.svelte";
import { DarkMode } from "flowbite-svelte";
import { MoonSolid, SunSolid } from "flowbite-svelte-icons";
</script>

<FunctionalIcon tooltip={'Darkmode ein- oder ausschalten'}>
    <DarkMode class="apply-icon-style">
        <MoonSolid slot="darkIcon" />
        <SunSolid slot="lightIcon" />
    </DarkMode>
</FunctionalIcon>
