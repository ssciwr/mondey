<svelte:options runes={true}/>

<script lang="ts">
import {
	getMilestoneAnswerSessionAnalysis,
	modifyMilestoneAnswerSession,
} from "$lib/client/sdk.gen";
import type { MilestoneAnswerSessionAnalysis } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import PlotSessionAnalysis from "$lib/components/DataDisplay/PlotSessionAnalysis.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { Alert, Button, Modal, Spinner } from "flowbite-svelte";
import { ThumbsDownOutline, ThumbsUpOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

let {
	open = $bindable(false),
	answer_session_id = null as number | null,
	callback,
}: {
	open: boolean;
	answer_session_id: number | null;
	callback: () => Promise<void>;
} = $props();

let analysis = $state(null as null | MilestoneAnswerSessionAnalysis);

async function set_suspicious(suspicious: boolean) {
	if (!answer_session_id) {
		return;
	}
	const { data, error } = await modifyMilestoneAnswerSession({
		path: {
			answer_session_id: answer_session_id,
		},
		query: {
			suspicious: suspicious,
		},
	});
	if (error || !data) {
		console.log(error);
		alertStore.showAlert(i18n.tr.admin.error, i18n.tr.admin.error, true, false);
	} else {
		await callback();
	}
	open = false;
}

onMount(async () => {
	if (answer_session_id) {
		const { data, error } = await getMilestoneAnswerSessionAnalysis({
			path: {
				answer_session_id: answer_session_id,
			},
		});
		if (error || !data) {
			console.log(error);
		} else {
			analysis = data;
		}
	}
});
</script>

<Modal bind:open outsideclose size="lg" title={`${i18n.tr.admin.milestoneAnswerSession} ${answer_session_id}`}>
    {#if !analysis}
        <Spinner/>
    {:else}
        <Alert color="dark">
            <div class="flex flex-row justify-around">
                <div>
                    {i18n.tr.admin.rmsDifferenceFromAverageScore}: <span
                        class={`text-lg font-bold ${analysis.rms>=1 ? 'text-red-700' : 'text-green-700'}`}>{ Number(analysis.rms).toFixed(2) }</span>
                </div>
                <div>
                    {i18n.tr.admin.childAgeMonths}: <span class="text-lg font-bold">{analysis?.child_age}</span>
                </div>
            </div>
        </Alert>
        <PlotSessionAnalysis data={analysis.answers}/>
    {/if}
    <svelte:fragment slot="footer">
        <Button color="green" data-testid="markNotSuspicious" onclick={async () => {await set_suspicious(false)}}>
            <ThumbsUpOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.notSuspicious}
        </Button>
        <Button color="red" data-testid="markSuspicious" onclick={async () => {await set_suspicious(true)}}>
            <ThumbsDownOutline class="me-2 h-5 w-5"/>{i18n.tr.admin.suspicious}
        </Button>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>
