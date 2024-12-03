<svelte:options runes={true} />
<script lang="ts">
import {
	type AgeInterval,
	createAgeInterval,
	updateAgeInterval,
} from "$lib/client";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import { Heading, Modal, Range } from "flowbite-svelte";
import { _ } from "svelte-i18n";

let {
	open = $bindable(false),
	interval = $bindable(null),
}: { open: boolean; interval: AgeInterval | null } = $props();

let showAlert = $state(false);
let alertMessage = $state($_("userData.alertMessageError"));
let lower = $state(interval === null ? 0 : interval.lower_limit);
let higher = $state(interval === null ? 0 : interval.upper_limit);

async function saveChanges(): Promise<void> {
	if (interval === null) {
		const response = await createAgeInterval({
			query: {
				high: higher,
				low: lower,
			},
		});

		if (response.error) {
			console.log("Error in creating age interval");
			showAlert = true;
			alertMessage = `${$_("userData.alertMessageError")} ${response.error.detail}`;
		} else {
			interval = response.data as AgeInterval;
			open = false;
		}
	} else {
		const response = await updateAgeInterval({
			path: {
				age_interval_id: interval.id as number,
			},
			query: {
				high: higher,
				low: lower,
			},
		});

		if (response.error) {
			console.log("Error in updating age interval");
			showAlert = true;
			alertMessage = `${$_("userData.alertMessageError")} ${response.error.detail}`;
		} else {
			interval = response.data as AgeInterval;
			open = false;
		}
	}
}
</script>

<Modal bind:open={open} title={$_("milestone.newAgeInterval")} size="xl" outsideclose>
    {#if showAlert}
        <AlertMessage
            title={$_("userData.alertMessageTitle")}
            message={alertMessage}
            onclick={() => {
                showAlert = false;
            }}
        />
    {/if}
    <div class="p-4 ">
        <Heading tag="h4" color="text-gray-700 dark:text-gray-400"
		class="block m-2">{$_("milestone.lowerAgeboundHeading")}</Heading>
        <p class = "m-2 p-2">{$_('milestone.lowerAgeboundExplanation')}</p>
		<p class = "m-2 p-2">{$_("milestone.currentValue")} : {lower}</p>
        <Range id="lowerBoundInput" min={1} max="72" bind:value={lower}/>
	</div>
    <div class="p-4 ">
        <Heading tag="h4" color="text-gray-700 dark:text-gray-400"
 		class="block m-2">{$_("milestone.upperAgeboundHeading")}</Heading>
        <p class = "m-2 p-2">{$_("milestone.upperAgeBoundExplanation")}</p>
		<p class = "m-2 p-2">{$_("milestone.currentValue")} : {higher}</p>
        <Range id="upperBoundInput" min={1} max="72" bind:value={higher}/>
    </div>

	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges} disabled = {lower >= higher}/>
		<CancelButton onclick={() => {open = false;}} />
	</svelte:fragment>
</Modal>
