<svelte:options runes={true}/>

<script lang="ts">
import { Tooltip } from "flowbite-svelte";

let {
	selected = false,
	index = 0,
	tooltip = "",
	onClick = () => {
		console.log("Button clicked");
	},
	children,
}: {
	selected: boolean;
	index: number;
	tooltip: string;
	onClick: () => void;
	children: any;
} = $props();

let bg_color = `bg-milestone-answer-${index}`;
const text_color = index < 2 ? 'dark:text-black' : 'dark:text-white';
</script>

<button
	type="button"
	onclick={onClick}
	class={`${bg_color} ${text_color} ${selected ? 'opacity-100 outline-none ring-4 ring-blue-400' : 'opacity-75 hover:opacity-100'} border-1 m-1 rounded-lg border border-gray-200 px-5 py-3 text-center font-medium md:my- `}
>
	{@render children?.()}
</button>
<Tooltip class={`${bg_color} text-gray-700 dark:${bg_color} dark:text-gray-700`}>
	{tooltip}
</Tooltip>
