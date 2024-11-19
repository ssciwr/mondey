<svelte:options runes={true} />
<script lang="ts">
import {
	type GetFeedbackForMilestonegroupResponse,
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

	const feedbackMilestoneGroup = await getMilestoneGroups({
		path: { child_id: currentChild.id as number },
	});
	if (feedbackMilestoneGroup.error) {
		showAlert = true;
		alertMessage = feedbackMilestoneGroup.error.detail;
		return;
	}
	const milestoneGroups = feedbackMilestoneGroup.data;
	console.log("milestonegroups: ", milestoneGroups);

	const responseFeedback = await getFeedbackForMilestonegroup({
		path: {
			child_id: currentChild.id,
			milestonegroup_id: milestoneGroups[0].id,
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
	feedbackMilestoneGroups = responseFeedback.data;
	console.log("responseFeedback: ", responseFeedback.data);
}

function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [dateObj.getDay(), dateObj.getMonth(), dateObj.getFullYear()].join(
		"-",
	);
}

const promise = setup();
let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | undefined,
);
let answerSessions = $state([] as MilestoneAnswerSessionPublic[]);
let feedbackMilestoneGroups = $state(
	{} as GetFeedbackForMilestonegroupResponse,
);
</script>

{#await promise}
<Spinner /> {$_("childData.loadingMessage")}
{:then _}
<div>
    <Timeline>
        <TimelineItem title = {'bla'} date = {formatDate(answerSessions[0].created_at)}/>
    </Timeline>
</div>
{:catch error}
<AlertMessage
    message = {alertMessage}
    title = {$_("childData.alertMessageTitle")}
/>
{/await}
