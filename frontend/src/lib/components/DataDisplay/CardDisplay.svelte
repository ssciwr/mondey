<script>
	import { Button, Card, Progressbar, Tooltip } from "flowbite-svelte";
	export let data = {
		header: undefined,
		summary: undefined,
		button: undefined,
		href: undefined,
		image: undefined,
		progress: undefined,
		events: undefined,
	};
	
	export let styleProps = {
		card: {},
		header: {},
		summary: {},
		button: {},
		progress: {},
	};
	
	// TODO: generalize event passing. currently only the on:click event is exposed
	</script>
	
	<Card
		img={data.image}
		imgClass="max-md:hidden object-scale-down"
		href={data.button ? null : data.href}
		class={data.button
			? 'm-2 max-w-prose min-w-full justify-center bg-[#a4d2d0] items-center text-gray-700 dark:text-white'
			: 'hover:transition-color m-2 max-w-prose cursor-pointer items-center text-gray-700 hover:bg-gray-300 dark:text-white dark:hover:bg-gray-600 '}
		{...styleProps.card}
		on:click={data.events['onclick']}
	>
		{#if data.header}
			<h5 class="mb-2 mt-3 text-center text-2xl font-bold tracking-wide" {...styleProps.header}>
				{data.header}
			</h5>
		{/if}
		{#if data.summary}
			<p class=" mb-7 flex text-center text-md leading-tight" {...styleProps.summary}>
				{data.summary}
			</p>
		{/if}
		{#if data.button}
			<Button
				href={data.href}
				class="w-44 mb-3 font-bold text-md bg-white text-gray-700"
				{...styleProps.button}
				on:click={data.button.events.onclick}
				>{data.button}
	
				{#if data.buttonIcon}
					<svelte:component this={data.buttonIcon} class="ms-2 h-6 w-6 text-gray-700" />
				{/if}
			</Button>
			<Tooltip>Anmelden oder ein neues Konto erstellen</Tooltip>
		{/if}
	
		{#if data.progress}
			<Progressbar
				labelInside
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
	