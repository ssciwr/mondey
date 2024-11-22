<svelte:options runes={true} />
<script lang="ts">
import { Accordion, AccordionItem, Modal, Spinner } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "../AlertMessage.svelte";

let {
	open = $bindable(false),
	session_id = $bindable(null),
	milestonegroup_id = $bindable(null),
}: {
	open: boolean;
	session_id: number | null;
	milestonegroup_id: number | null;
} = $props();

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | undefined,
);

async function setup(): Promise<Record<number, number>> {
	console.log("setup");
	const detailedFeedbackresponse = await getDetailedFeedbackForMilestonegroup({
		path: {
			answersession_id: session_id,
			milestonegroup_id: milestonegroup_id,
		},
	});
	if (detailedFeedbackresponse.error) {
		console.log(detailedFeedbackresponse.error);
		return {};
	}
	return detailedFeedbackresponse.data;
}

let promise = setup();
</script>

{#await promise}
<div class = "flex justify-center items-center flex-row">
	<Spinner /> <p>{$_("childData.loadingMessage")}</p>
</div>
{:then detailedFeedback}
{#if showAlert }
<AlertMessage title = {$_("childData.alertMessageTitle")} message = {alertMessage} />
{/if}
<Modal open={open}>
    <Accordion>
        {#each Object.keys(detailedFeedback) as key}
        <AccordionItem >
            <span slot="header">{key}</span>
            <p>{detailedFeedback[key]}</p>
        </AccordionItem>
        {/each}
    </Accordion>
</Modal>
{:catch error}
<AlertMessage
    message = {`${alertMessage} ${error}`}
    title = {$_("childData.alertMessageTitle")}
/>
{/await}
