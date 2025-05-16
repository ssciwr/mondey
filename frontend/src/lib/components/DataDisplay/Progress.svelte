<svelte:options runes={true}/>
<script lang="ts">
import { Progressbar } from "flowbite-svelte";
let { progress = 0.0 }: { progress: number } = $props();

let displayProgress = $derived(progress < 0.01 ? 1 : 100 * progress);
</script>

<div class="rounded-lg bg-white p-2 pb-4 w-full">
    <Progressbar
            animate={true}
            color={displayProgress === 100 ? 'green' : 'red'}
            divClass={`h-full rounded-full w-${displayProgress}`}
            labelInside={true}
            labelInsideClass={`${progress === 100 ? 'text-white' : 'text-black'} rounded-md text-small pl-2`}
            progress={`${displayProgress}`}
            size="h-4"
    />
</div>
