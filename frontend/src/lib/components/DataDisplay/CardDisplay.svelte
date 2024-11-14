<svelte:options runes={true} />
<script lang="ts">
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
	},
	styleProps = {
		card: {},
		header: {},
		summary: {},
		button: {},
		progress: {},
	},
}: { data: any; styleProps: any } = $props();
</script>

<Card
	img={data.image}
	imgClass="max-md:hidden object-scale-down"
	href={data.button ? null : data.href}
	class={data.button
		? 'm-2 max-w-prose items-center  text-gray-700 dark:text-white'
		: 'hover:transition-color m-2 max-w-prose cursor-pointer items-center text-gray-700 hover:bg-gray-300 dark:text-white dark:hover:bg-gray-600 '}
	{...styleProps.card}
	on:click={data.events['onclick']}
>
	{#if data.header}
		<h5 class="mb-2 text-2xl font-bold tracking-tight" {...styleProps.header}>
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
			on:click={data.button.events.onclick}
			>{data.button}

			{#if data.buttonIcon}
				<svelte:component this={data.buttonIcon} class="ms-2 h-6 w-6 text-white" />
			{:else}
				<ArrowRightOutline class="ms-2 h-6 w-6 text-white" />
			{/if}
		</Button>
		<Tooltip>Fortfahren</Tooltip>
	{/if}

	{#if data.progress}
		<Progressbar
			labelInside ={styleProps.progress?.labelInside}
			progress={String(100 * data.progress)}
			animate={true}
			color={data.progress === 1 ? styleProps.progress?.completeColor : styleProps.progress?.color}
			size={styleProps.progress?.size}
			divClass={styleProps?.progress.divClass}
			labelInsideClass={styleProps.progress?.labelInsideClass}
		/>
	{/if}

	<!-- This will be generalized to replace button and progressbar later  -->
	{#if data.auxilliary}
		<div class="mb-4 mt-auto flex w-full justify-center">
			<svelte:component this={data.auxilliary} {...styleProps.auxilliary} />
		</div>
	{/if}
</Card>
