<svelte:options runes={true} />

<script lang="ts">
import { getEvents } from "$lib/client/sdk.gen";
import type { CalendarEventRead } from "$lib/client/types.gen";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Card } from "flowbite-svelte";
import { LinkOutline } from "flowbite-svelte-icons";

async function loadCalendarEvents(): Promise<
	Record<number, CalendarEventRead[]>
> {
	const { data, error: apiError } = await getEvents();
	if (apiError || data === undefined) {
		throw new Error(
			`Failed to load calendar events: ${apiError || "Unknown error"}`,
		);
	}

	const sortedEvents = data.sort(
		(a, b) =>
			new Date(a.event_date).getTime() - new Date(b.event_date).getTime(),
	);

	const eventsByYear: Record<number, CalendarEventRead[]> = {};
	sortedEvents.forEach((event) => {
		const year = new Date(event.event_date).getFullYear();
		if (!eventsByYear[year]) {
			eventsByYear[year] = [];
		}
		eventsByYear[year].push(event);
	});

	return eventsByYear;
}

function formatDay(dateString: string): string {
	const date = new Date(dateString);
	return String(date.getDate());
}

function formatMonth(dateString: string): string {
	const date = new Date(dateString);
	return date.toLocaleDateString(undefined, { month: "short" });
}

const calendarEventsPromise = loadCalendarEvents();
</script>

<div class="space-y-6">
	<div class="border-b-4 border-primary-600 pb-4">
		<h2 class="text-2xl font-bold text-gray-900">{i18n.tr.frontpage.upcomingEvents}</h2>
	</div>

	{#await calendarEventsPromise}
		<div class="flex justify-center items-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
		</div>
	{:then eventsByYear}
		{#if Object.keys(eventsByYear).length === 0}
			<Card class="text-center py-8">
				<p class="text-gray-500">{i18n.tr.frontpage.noEventsFound}</p>
			</Card>
		{:else}
			{#each Object.entries(eventsByYear).sort(([a], [b]) => Number(a) - Number(b)) as [year, yearEvents]}
				<div class="space-y-4">
					<h3 class="text-3xl font-bold text-gray-800 pb-4">{year}</h3>
					
					{#each yearEvents as calendarEvent (calendarEvent.id)}
						<div class="flex gap-4 sm:gap-6 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
							<div class="flex flex-col items-center justify-start min-w-[50px] sm:min-w-[60px]">
								<div class="text-2xl sm:text-3xl font-bold text-gray-900">
									{formatDay(calendarEvent.event_date)}
								</div>
								<div class="text-xs sm:text-sm text-gray-600 uppercase">
									{formatMonth(calendarEvent.event_date)}
								</div>
							</div>

							<div class="w-px bg-gray-300 self-stretch"></div>

							<div class="flex-1 min-w-0">
								<div class="flex items-start justify-between gap-4">
									<div class="flex-1">
										{#if calendarEvent.title}
											<h3 class="text-xl font-semibold text-gray-900 leading-tight mb-1">
												{calendarEvent.title}
											</h3>
										{/if}

										{#if calendarEvent.description}
											<p class="text-gray-600 leading-relaxed">
												{calendarEvent.description}
											</p>
										{/if}
									</div>

									{#if calendarEvent.external_link}
										<a 
											href={calendarEvent.external_link}
											target="_blank"
											rel="noopener noreferrer"
											class="text-gray-400 hover:text-primary-600 transition-colors flex-shrink-0"
											aria-label="External link"
										>
											<LinkOutline size="sm" />
										</a>
									{/if}
								</div>

								{#if calendarEvent.external_link}
									<div class="mt-3">
										<a
											href={calendarEvent.external_link}
											target="_blank"
											rel="noopener noreferrer"
											class="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 transition-colors text-sm font-medium"
										>
											<LinkOutline size="xs" />
											Learn more
										</a>
									</div>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{/each}
		{/if}
	{:catch error}
		<AlertMessage message={`${i18n.tr.frontpage.eventsLoadError}: ${error.message}`} isError={true} />
	{/await}
</div>