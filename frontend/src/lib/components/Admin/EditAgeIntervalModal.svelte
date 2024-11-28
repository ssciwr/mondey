<svelte:options runes={true} />
<script lang="ts">
import { createAgeInterval } from "$lib/client";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import { Label, Modal, Range } from "flowbite-svelte";
import { _ } from "svelte-i18n";

let {
	show = $bindable(false),
	interval = $bindable({} as AgeIntervalPublic),
}: { show: boolean; interval: AgeIntervalPublic } = $props();
let showAlert = $state(false);
let alertMessage = $state($_("userData.alertMessageError"));

async function saveChanges(): Promise<void> {
	if (interval.upper_limit < interval.lower_limit) {
		console.log("Upper bound must be greater than lower bound");
	} else {
		const submitResponse = await createAgeInterval({
			query: {
				lower_limit: interval.lower_limit,
				upper_limit: interval.upper_limit,
			},
		});

		if (submitResponse.error) {
			console.log("Error in creating age interval");
			showAlert = true;
			alertMessage = `${$_("userData.alertMessageError")} ${submitResponse.error.detail}`;
		} else {
			show = false;
		}
	}
}
</script>

<Modal bind:open={show} title={$_("milestone.newAgeInterval")} size="xl" outsideclose>
    {#if showAlert}
        <AlertMessage
            title={$_("userData.alertMessageTitle")}
            message={alertMessage}
            onclick={() => {
                showAlert = false;
            }}
        />
    {/if}

    <div class="p-4">
        <Label for="lowerBoundInput" class="block mb-2">{$_("milestone.lowerAgeboundHeading")}</Label>
        <p>{$_('milestone.lowerAgeboundExplanation')}: {interval.lower_limit}</p>
        <Range id="expected-age-months" min="1" max="72" bind:value={interval.lower_limit}/>

        <Label for="upperBoundInput" class="block mb-2">{$_("milestone.upperAgeboundHeading")}</Label>
        <p>$_{"milestone.upperBoundExplanation"}: {interval.upper_limit}</p>
        <Range id="expected-age-months" min={String(interval.lower_limit)} max="72" bind:value={interval.upper_limit}/>
    </div>
	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges} />
		<CancelButton onclick={() => {show = false;}}/>
	</svelte:fragment>
</Modal>
