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
        <!--Color the interval between the-->
        <div class = "absolute bg-gray-400 dark:bg-gray-700 h-5" style="left: calc((100% / 72) * {lower}); width: calc((100% / 72) * {upper - lower})" >

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
    -webkit-appearance: none; /* For Chrome */
    -moz-appearance: none;    /* For Firefox */
    appearance: none;
    width: 100%;
    height: 0; /* Hide the native slider track */
    background: transparent;
    margin: 0; /* Remove default margin */
    padding: 0; /* Remove default padding */
    }

    /* Remove default track styles */
    input[type="range"]::-webkit-slider-runnable-track {
    height: 0;
    background: transparent;
    border: none;
    }

    input[type="range"]::-moz-range-track {
    height: 0;
    background: transparent;
    border: none;
    }

    /* Remove default thumb outline in Firefox */
    input[type="range"]::-moz-focus-outer {
    border: 0;
    }


    /* Base slider thumb styles */
    input[type="range"]::-webkit-slider-thumb {
        width: 1.25rem; /* Adjust size as needed */
        height: 1.25rem;
        background:transparent;
        cursor: pointer;
        border: none;
    }
    input[type="range"]::-moz-range-thumb {
        width: 1.25rem; /* Adjust size as needed */
        height: 1.25rem;
        background:transparent;
        cursor: pointer;
        border: none;
    }

    /* Specific styles for 'slider-lower' thumb */
    #slider-lower::-webkit-slider-thumb {
        background: #FF0000;
        clip-path: polygon(0% 0%, 0% 100%, 100% 50%); /* Triangle pointing right */
    }

    #slider-lower::-moz-range-thumb {
        background: #FF0000;
        clip-path: polygon(0% 0%, 0% 100%, 100% 50%); /* Triangle pointing right */
    }

    /* Specific styles for 'slider-upper' thumb */
    #slider-upper::-webkit-slider-thumb {
        background: #00FF00;
        clip-path: polygon(100% 0%, 100% 100%, 0% 50%); /* Triangle pointing left */
    }

    #slider-upper::-moz-range-thumb {
        background: #00FF00;
        clip-path: polygon(100% 0%, 100% 100%, 0% 50%); /* Triangle pointing left */
    }

    /* Specific styles for 'slider-central' thumb */
    #slider-central::-webkit-slider-thumb {
        background: #4A90E2;
        clip-path: polygon(20% 0%, 0% 20%, 30% 50%, 0% 80%, 20% 100%, 50% 70%, 80% 100%, 100% 80%, 70% 50%, 100% 20%, 80% 0%, 50% 30%); /* Triangle pointing up */
    }
    #slider-central::-moz-range-thumb {
        background: #4A90E2;
        clip-path: polygon(20% 0%, 0% 20%, 30% 50%, 0% 80%, 20% 100%, 50% 70%, 80% 100%, 100% 80%, 70% 50%, 100% 20%, 80% 0%, 50% 30%); /* Triangle pointing up */
    }

    /* Remove the default blue range progress in Firefox */
    input[type="range"]::-moz-range-progress {
        background: transparent;
        border: none;
    }

</style>
