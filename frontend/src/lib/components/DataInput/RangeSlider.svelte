<svelte:options runes={true}/>
<script lang="ts">
let {
	lower = $bindable(0),
	upper = $bindable(72),
	central = $bindable(36),
	divClass = "",
}: {
	lower: number;
	upper: number;
	central: number;
	divClass: string;
} = $props();

function handleLowerInput(event: Event) {
	if (event.target !== null) {
		lower = Math.min(Number(event.target.value), central - 1);
	}
}

function handleUpperInput(event: Event) {
	if (event.target !== null) {
		upper = Math.max(Number(event.target.value), central + 1);
	}
}

function handleCentralInput(event: Event) {
	if (event.target !== null) {
		const old_central = central;
		central = Number(event.target.value);
		upper = upper + (central - old_central);
		lower = lower + (central - old_central);
	}
}

$effect(() => {
	console.log(lower, central, upper);
});
</script>

<div class={"relative w-full h-12 " + divClass}>
    <input
        id="slider-lower"
        class="absolute w-full bg-transparent appearance-none cursor-pointer z-30 h-2"
        type="range"
        min="0"
        max="72"
        step="1"
        value={lower}
        oninput={handleLowerInput}
    />

    <input
        id="slider-upper"
        class="absolute w-full bg-transparent appearance-none cursor-pointer z-20 h-2 "
        type="range"
        min="0"
        max="72"
        step="1"
        value={upper}
        oninput={handleUpperInput}
    />

    <input
        id="slider-central"
        class="p-2 m-2 absolute w-full rounded-md bg-gray-50 dark:bg-gray-600 text-gray-900 dark:text-white appearance-none cursor-default z-10 h-2"
        type="range"
        min="0"
        max="72"
        step="1"
        value={central}
        oninput={handleCentralInput}
    />
</div>

<style>
    input[type="range"]::-webkit-slider-runnable-track {
        height: 0;
        background: transparent;
    }
    input[type="range"]::-moz-range-track {
        height: 0;
        background: transparent;
    }
</style>
