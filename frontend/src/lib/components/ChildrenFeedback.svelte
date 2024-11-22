<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	getExpiredMilestoneAnswerSessions,
	getFeedbackForMilestonegroup,
	getMilestoneGroups,
} from "$lib/client";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Spinner, Timeline, TimelineItem } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

async function setup(): Promise<void> {
	user.load;
	await currentChild.load_data();

	if (currentChild.id === null || user.id === null) {
		showAlert = true;
		return;
	}
	const responseAnswerSessions = await getExpiredMilestoneAnswerSessions({
		path: { child_id: currentChild.id as number },
	});
	if (responseAnswerSessions.error) {
		showAlert = true;
		alertMessage = responseAnswerSessions.error.detail;
		return;
	}
	answerSessions = responseAnswerSessions.data;
	console.log("answerSessions: ", answerSessions);

	const responseMilestoneGroups = await getMilestoneGroups({
		path: { child_id: currentChild.id as number },
	});
	if (responseMilestoneGroups.error) {
		showAlert = true;
		alertMessage = feedbackMilestoneGroup.error.detail;
		return;
	}
	const milestoneGroups = responseMilestoneGroups.data;
	console.log("milestonegroups: ", milestoneGroups);

	for (const milestonegroup of milestoneGroups) {
		const responseFeedback = await getFeedbackForMilestonegroup({
			path: {
				child_id: currentChild.id,
				milestonegroup_id: milestonegroup.id,
			},
			query: {
				with_detailed: true,
			},
		});
		if (responseFeedback.error) {
			showAlert = true;
			alertMessage = responseFeedback.error.detail;
			return;
		}

		feedbackMilestoneGroups[milestonegroup.id] = responseFeedback.data;
		console.log("responseFeedback: ", responseFeedback.data);
	}
}

function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [
		dateObj.getDate(),
		dateObj.getMonth() + 1,
		dateObj.getFullYear(),
	].join("-");
}

const promise = setup();
let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | undefined,
);
let answerSessions = $state([] as MilestoneAnswerSessionPublic[]);
let feedbackMilestoneGroups = $state({});
</script>

{#await promise}
<Spinner /> {$_("childData.loadingMessage")}
{:then _}
<div>
    <Timeline>
		{#each answerSessions as answerSession}
        <TimelineItem  date = {formatDate(answerSession.created_at)}/>
			{#each Object.entries(feedbackMilestoneGroups) as [mid, feedback]}
				{#if formatDate(answerSession.created_at) in feedback}
					{mid, 'total: ', feedback[formatDate(answerSession.created_at)][0]}
					{console.log(mid, feedback)}
				{/if}
			{/each}
		{/each}
    </Timeline>
</div>
{:catch error}
<AlertMessage
    message = {`${alertMessage} ${error}`}
    title = {$_("childData.alertMessageTitle")}
/>
{/await}
