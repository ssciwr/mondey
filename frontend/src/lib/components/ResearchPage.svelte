<svelte:options runes={true}/>

<script lang="ts">
import {getResearchData} from "$lib/client/services.gen";
import {type GetResearchDataResponse} from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { onMount } from "svelte";

let data = $state([] as GetResearchDataResponse);

async function refreshData() {
    const res = await getResearchData();
    if(res.error || !res.data) {
        console.error(res.error);
        return;
    }
    data = res.data
}

onMount(async () => {
	await user.load();
	await refreshData();
});

</script>

{#each data as row}
    <div>
        <p>{row}</p>
    </div>
{/each}