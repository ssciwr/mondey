<svelte:options runes={true}/>
<script lang="ts">
import { Progressbar } from "flowbite-svelte";
let { progress = 0.0, color = "red" }: { progress: number; color: string } =
	$props();

let displayProgress = $derived(progress < 0.01 ? 1 : 100 * progress);

const dynamicColorClass = `dynamic-bg-color-${id}`;

let wrapperStyle = $derived(`--dynamic-bg-color-${id}: ${color};`);

let labelClass = $derived(
	progress === 100
		? "text-white rounded-md text-small pl-2 bg-green"
		: `text-black rounded-md text-small pl-2 ${dynamicColorClass}`,
);
</script>

<div class="rounded-lg bg-white p-2 pb-4 w-full" style={wrapperStyle}>
    <Progressbar
            animate={true}
            divClass={`h-full rounded-full w-${displayProgress}`}
            labelInside={true}
            labelInsideClass={labelClass}
            progress={`${displayProgress}`}
            size="h-4"
    />
</div>

<style>
    /* Dynamic selector based on the instance ID */
    :global(.dynamic-bg-color-progress-1) {
        background-color: var(--dynamic-bg-color-progress-1);
    }
</style>
