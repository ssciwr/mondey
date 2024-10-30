<script lang="ts">
import { Tooltip } from "flowbite-svelte";

export let selected = false;
export let index: number;
export let tooltip = "";
export let onClick: () => void;

let bg_color = `bg-milestone-answer-${index}`;
</script>

<button
	type="button"
	on:click={onClick}
	class={`${bg_color} ${selected ? 'opacity-100 outline-none ring-4 ring-blue-400' : 'opacity-50 hover:opacity-80'} border-1 m-1 rounded-lg border border-gray-200 px-5 py-3 text-center font-medium md:my-2`}
>
	<slot />
</button>
<Tooltip class={`${bg_color} text-gray-700 dark:${bg_color} dark:text-gray-700`}>
	{tooltip}
</Tooltip>
