<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	getExpiredMilestoneAnswerSessions,
	getSummaryFeedbackForAnswersession,
} from "$lib/client";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Spinner, Timeline, TimelineItem } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | undefined,
);
let answerSessions = $state([] as MilestoneAnswerSessionPublic[]);
let feedbackPerAnswersession = $state({} as Record<number, any>);

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

	for (const answersession of answerSessions) {
		const responseFeedback = await getSummaryFeedbackForAnswersession({
			path: {
				answersession_id: answersession.id,
			},
		});

		if (responseFeedback.error) {
			showAlert = true;
			alertMessage = responseFeedback.error.detail;
			return;
		}
		feedbackPerAnswersession[answersession.id] = responseFeedback.data;
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
</script>

{#await promise}
<div class = "flex justify-center items-center ">
<Spinner /> <p>{$_("childData.loadingMessage")}</p>
</div>
{:then _}
<div>
    <Timeline>
		{#each answerSessions as answersession}
        <TimelineItem  date = {formatDate(answersession.created_at)}/>
		<div class = "">
			feedback goes here
			{console.log(answersession.id, ": ", feedbackPerAnswersession[answersession.id] )}
		</div>
		{/each}
    </Timeline>
</div>
{:catch error}
<AlertMessage
    message = {`${alertMessage} ${error}`}
    title = {$_("childData.alertMessageTitle")}
/>
{/await}
