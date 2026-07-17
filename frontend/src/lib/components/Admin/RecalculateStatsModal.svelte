<svelte:options runes={true}/>

<script lang="ts">
import { adminUpdateStats } from "$lib/client/sdk.gen";
import { i18n } from "$lib/i18n.svelte";
import { Button, Modal, Spinner } from "flowbite-svelte";
import { CloseOutline } from "flowbite-svelte-icons";

let {
	open = $bindable(false),
	// optional confirmation prompt shown before recalculating: if set, the user is
	// asked to confirm first; if omitted, the recalculation starts as soon as the modal opens
	prompt = "",
	oncompleted = undefined,
}: {
	open?: boolean;
	prompt?: string;
	oncompleted?: () => void;
} = $props();

let running: boolean = $state(false);
let finished: boolean = $state(false);
let message: string = $state("");

async function recalculate() {
	running = true;
	finished = false;
	message = "";
	try {
		const { data, error } = await adminUpdateStats();
		if (error || !data) {
			console.log(error);
			message = i18n.tr.admin.error;
			return;
		}

		// Build a localized summary from the structured result returned by the backend.
		message =
			`${i18n.tr.admin.statisticsRecalculated} ` +
			`${data.answer_sessions} ${i18n.tr.admin.milestoneAnswerSessions}, ` +
			`${data.answers} ${i18n.tr.admin.answers}, ` +
			`${data.runtime_seconds.toFixed(1)} ${i18n.tr.admin.seconds}.`;
		oncompleted?.();
	} catch (error) {
		console.log(error);
		message = i18n.tr.admin.error;
	} finally {
		running = false;
		finished = true;
	}
}

$effect(() => {
	if (open) {
		// with no confirmation prompt, start the recalculation immediately
		if (!prompt && !running && !finished) {
			recalculate();
		}
	} else if (!running) {
		// reset when closed, ready for next time
		finished = false;
		message = "";
	}
});
</script>

<Modal bind:open size="md" title={i18n.tr.admin.updateStatistics} dismissable={!running}>
    {#if running}
        <div class="flex items-center">
            <Spinner class="me-2 h-5 w-5"/>{i18n.tr.admin.statisticsAreBeingUpdated}
        </div>
    {:else if finished}
        {message}
    {:else if prompt}
        {prompt}
    {/if}
    <svelte:fragment slot="footer">
        {#if prompt && !running && !finished}
            <Button data-testid="recalculateStatsButton" onclick={recalculate}>
                {i18n.tr.admin.recalculateNow}
            </Button>
            <Button color="alternative" onclick={() => {open = false;}}>
                {i18n.tr.admin.recalculateLater}
            </Button>
        {:else}
            <Button color="alternative" onclick={() => {open = false;}} disabled={running}>
                <CloseOutline class="me-2 h-5 w-5" data-testid="closeUpdateStatsModal"/> {i18n.tr.admin.close}
            </Button>
        {/if}
    </svelte:fragment>
</Modal>
