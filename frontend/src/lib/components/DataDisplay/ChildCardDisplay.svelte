<svelte:options runes={true}/>
<script lang="ts">
import { goto } from "$app/navigation";
import type { ChildSummaryPublic } from "$lib/client/types.gen";
import CardDisplay from "$lib/components/DataDisplay/CardDisplay.svelte";
import Progress from "$lib/components/DataDisplay/Progress.svelte";
import TimeRemaining from "$lib/components/DataDisplay/TimeRemaining.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";

let { child }: { child: ChildSummaryPublic } = $props();

async function onclick() {
	currentChild.id = child.id;
	await currentChild.load_data();
	goto("/userLand/children/registration");
}
</script>

<CardDisplay title={child.name} text={`${child.birth_month}/${child.birth_year}`} color={child.color} image={child.image} {onclick}>
    {#if child.active_answer_session}
        <Progress progress={child.session_progress} />
        <TimeRemaining secondsRemaining={child.session_remaining_seconds}/>
    {/if}
</CardDisplay>
