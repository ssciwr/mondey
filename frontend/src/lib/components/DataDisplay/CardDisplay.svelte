<svelte:options runes={true} />
<script lang="ts">
import { type CardElement, type CardStyle } from "$lib/util";
import { Button, Card, Progressbar, Tooltip } from "flowbite-svelte";
import { ArrowRightOutline } from "flowbite-svelte-icons";

let {
	data = {
		header: undefined,
		summary: undefined,
		button: undefined,
		href: undefined,
		image: undefined,
		progress: undefined,
		events: undefined,
		auxilliary: undefined,
		buttonIcon: undefined,
	},
	styleProps = {
		card: {},
		header: {},
		summary: {},
		button: {},
		progress: null,
		auxilliary: {},
	},
}: { data: CardElement; styleProps: CardStyle } = $props();
</script>

<Card
	img={data.image}
	imgClass="max-md:hidden object-scale-down"
	href={data.button ? undefined : data?.href}
	class={data.button
		? 'm-2 max-w-prose items-center  text-gray-700 dark:text-white'
		: 'hover:transition-color m-2 max-w-prose cursor-pointer items-center text-gray-700 hover:bg-gray-300 dark:text-white dark:hover:bg-gray-600 '}
	{...styleProps.card}
	on:click={data?.events?.['onclick'] ?? (()=>{})}
>
	{#if data.header}
		<h5 class="mb-2 text-2xl font-bold tracking-tight " {...styleProps.header}>
			{data.header}
		</h5>
	{/if}
	{#if data.summary}
		<p class=" mb-3 flex font-normal leading-tight" {...styleProps.summary}>
			{data.summary}
		</p>
	{/if}
	{#if data.button}
		<Button
			href={data.href}
			class="w-fit"
			{...styleProps.button}
			on:click={data.button?.events.onclick ?? (()=>{})}
			>{data.button}

			{#if data.buttonIcon}
				<data.buttonIcon class="ms-2 h-6 w-6 text-white" />
			{:else}
				<ArrowRightOutline class="ms-2 h-6 w-6 text-white" />
			{/if}
		</Button>
		<Tooltip>Fortfahren</Tooltip>
	{/if}

	{#if data.progress}
		<div class="rounded-lg bg-white p-2 pb-4">
			<Progressbar
				labelInside ={styleProps.progress?.labelInside}
				progress={String(100 * data.progress)}
				animate={true}
				color={data.progress === 1 ? styleProps.progress?.completeColor : styleProps.progress?.color}
				size={styleProps.progress?.size}
				divClass={styleProps.progress?.divClass}
				labelInsideClass={`{styleProps.progress?.labelInsideClass} {data.progress === 1 ? 'text-white' : 'text-black'} rounded-md text-small pl-2`}
			/>
		</div>
	{/if}

	{#if data.auxilliary}
		<div class="mb-4 mt-auto flex w-full justify-center ">
			<div class="bg-white p-1 rounded-full">
				<data.auxilliary {...styleProps.auxilliary} />
			</div>
		</div>
	{/if}
</Card>
