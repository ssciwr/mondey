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

    <div class="rounded-md bg-gray-300 dark:bg-gray-600 h-5 w-full">
        <div class = "absolute bg-gray-400 dark:bg-gray-700 rounded-md h-5" style="width: calc((100% / 72) * {upper - lower})" >

        </div>
        <input
            id="slider-lower"
            class="absolute w-full bg-transparent appearance-none cursor-pointer z-30 h-0"
            type="range"
            min="0"
            max="72"
            step="1"
            value={lower}
            oninput={handleLowerInput}
        />

        <input
            id="slider-upper"
            class="absolute w-full bg-transparent appearance-none cursor-pointer z-20 h-0 "
            type="range"
            min="0"
            max="72"
            step="1"
            value={upper}
            oninput={handleUpperInput}
        />

        <input
            id="slider-central"
            class="absolute w-full bg-transparent appearance-none cursor-default h-0 z-10 "
            type="range"
            min="0"
            max="72"
            step="1"
            value={central}
            oninput={handleCentralInput}
        />
    </div>
</div>

<style>
    input[type="range"] {
        -webkit-appearance: none;
        appearance: none;
        width: 100%;
        height: 2px;
        background: transparent;
    }

    input[type="range"]::-webkit-slider-runnable-track {
        width: 100%;
        height: 2px;
        cursor: pointer;
        background: transparent;
    }

    /* make left slider a triangle pointing to the right*/
    #slider-lower::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%); /* Triangle shape right */
    }

    #slider-lower::-moz-range-thumb {
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%);  /* Triangle shape left */
    }

    /* make right slider a triangle pointing to the left*/
    #slider-upper::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(50% 0%, 50% 100%, 0% 50%);; /* Triangle shape right */
    }

    #slider-upper::-moz-range-thumb {
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(50% 0%, 50% 100%, 0% 50%);  /* Triangle shape left */
    }

    /*make the central slider a cross */

    #slider-central::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(20% 0%, 0% 20%, 30% 50%, 0% 80%, 20% 100%, 50% 70%, 80% 100%, 100% 80%, 70% 50%, 100% 20%, 80% 0%, 50% 30%); /* cross*/
    }

    #slider-central::-moz-range-thumb {
        width: 1.25rem;
        height: 1.25rem;
        cursor: pointer;
        clip-path: polygon(20% 0%, 0% 20%, 30% 50%, 0% 80%, 20% 100%, 50% 70%, 80% 100%, 100% 80%, 70% 50%, 100% 20%, 80% 0%, 50% 30%);  /* rectangle */
    }
</style>
