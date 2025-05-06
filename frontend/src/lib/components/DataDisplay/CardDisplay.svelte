<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { type CardElement, type CardStyle } from "$lib/util";
import { Button, Card, Progressbar, Tooltip } from "flowbite-svelte";
import { ArrowRightOutline, ClockOutline } from "flowbite-svelte-icons";
import { Duration } from "luxon";

let {
	data = {
		header: undefined,
		summary: undefined,
		button: undefined,
		href: undefined,
		image: undefined,
		progress: undefined,
		events: undefined,
		auxiliary: undefined,
		buttonIcon: undefined,
		secondsRemaining: undefined,
	},
	styleProps = {
		card: {},
		header: {},
		summary: {},
		button: {},
		progress: null,
		auxiliary: {},
	},
}: { data: CardElement; styleProps: CardStyle } = $props();

let remainingTimeAsString = $derived.by(() => {
	if (!data.secondsRemaining) {
		return "";
	}
	const duration = Duration.fromObject(
		{ seconds: data.secondsRemaining },
		{ locale: i18n.locale },
	)
		.shiftTo("days", "hours", "minutes")
		.normalize();
	const unit =
		duration.days > 0 ? "days" : duration.hours > 0 ? "hours" : "minutes";
	return duration.shiftTo(unit).toHuman({
		maximumFractionDigits: 0,
	});
});
</script>

<Card
        {...styleProps.card}
        class={data.button
       ? 'm-2 max-w-prose flex flex-col h-full text-gray-700 dark:text-white'
       : 'hover:transition-color m-2 max-w-prose flex flex-col h-full cursor-pointer text-gray-700 hover:bg-gray-300 dark:text-white dark:hover:bg-gray-600 '}
        href={data.button ? undefined : data?.href}
        img={data.image}
        imgClass="max-md:hidden object-scale-down"
        on:click={data?.events?.['onclick'] ?? (()=>{})}
>
    <!-- Fixed height container for header -->
    <div>
        {#if data.header}
            <h5 class="text-xl font-bold break-words hyphens-auto " {...styleProps.header}>
                {data.header}
            </h5>
        {/if}
    </div>

    <!-- Summary text starts at consistent height -->
    <div class="flex-grow">
        {#if data.summary}
            <p class="font-normal leading-tight" {...styleProps.summary}>
                {data.summary}
            </p>
        {/if}
    </div>

    <!-- Push all the following content to bottom -->
    <div class="mt-auto pt-4 flex flex-col">
        {#if data.button}
            <Button
                    href={data.href}
                    class="w-fit"
                    {...styleProps.button}
                    on:click={data.button?.events.onclick ?? (()=>{})}
            >{data.button}

                {#if data.buttonIcon}
                    <data.buttonIcon class="ms-2 h-6 w-6 text-white"/>
                {:else}
                    <ArrowRightOutline class="ms-2 h-6 w-6 text-white"/>
                {/if}
            </Button>
            <Tooltip>Fortfahren</Tooltip>
        {/if}

        {#if data.progress}
            <div class="rounded-lg bg-white p-2 pb-4 w-full">
                <Progressbar
                        labelInside={styleProps.progress?.labelInside}
                        progress={String(100 * data.progress)}
                        animate={true}
                        color={data.progress === 1 ? styleProps.progress?.completeColor : styleProps.progress?.color}
                        size={styleProps.progress?.size}
                        divClass={styleProps.progress?.divClass}
                        labelInsideClass={`{styleProps.progress?.labelInsideClass} {data.progress === 1 ? 'text-white' : 'text-black'} rounded-md text-small pl-2`}
                />
            </div>
        {/if}

        {#if remainingTimeAsString}
            <div class="flex flex-row pt-4">
                <ClockOutline class="me-2 h-6 w-6"/> {remainingTimeAsString}
            </div>
        {/if}

        {#if data.auxiliary}
            <div class="mb-4 flex w-full justify-center">
                <div class="p-1 rounded-full" style="border: 10px solid white">
                    <data.auxiliary {...styleProps.auxiliary}/>
                </div>
            </div>
        {/if}
    </div>
</Card>
