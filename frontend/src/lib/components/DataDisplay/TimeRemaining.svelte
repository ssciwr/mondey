<svelte:options runes={true}/>
<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { ClockOutline } from "flowbite-svelte-icons";
import { Duration, type DurationUnit } from "luxon";

let { secondsRemaining = 0.0 }: { secondsRemaining: number } = $props();

function bestDurationUnit(duration: Duration): DurationUnit {
	if (duration.days > 0) {
		return "days";
	}
	if (duration.hours > 0) {
		return "hours";
	}
	return "minutes";
}

let remainingTimeAsLocalisedString = $derived.by(() => {
	if (!secondsRemaining) {
		return "";
	}
	const duration = Duration.fromObject(
		{ seconds: secondsRemaining },
		{ locale: i18n.locale },
	)
		.shiftTo("days", "hours", "minutes")
		.normalize();
	return duration.shiftTo(bestDurationUnit(duration)).toHuman({
		maximumFractionDigits: 0,
	});
});
</script>

<div class="flex flex-row pt-4">
    <ClockOutline class="me-2 h-6 w-6"/> {remainingTimeAsLocalisedString}
</div>
