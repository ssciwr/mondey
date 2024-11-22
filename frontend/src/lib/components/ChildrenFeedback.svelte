<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	getExpiredMilestoneAnswerSessions,
	getMilestonegroupsForSession,
	getSummaryFeedbackForAnswersession,
} from "$lib/client";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Accordion,
	AccordionItem,
	Hr,
	Spinner,
	Timeline,
	TimelineItem,
} from "flowbite-svelte";
import {
	BellActiveSolid,
	CheckCircleSolid,
	CircleMinusSolid,
} from "flowbite-svelte-icons";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | undefined,
);
let answerSessions = $state({} as Record<number, MilestoneAnswerSessionPublic>);
let feedbackPerAnswersession = $state({} as Record<number, any>);
let milestongeGroups = $state({} as Record<number, any>);
let sessionkeys = $state([] as number[]);

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
	sessionkeys = Object.keys(answerSessions)
		.sort()
		.reverse()
		.map((x) => Number(x));

	for (const aid of Object.keys(answerSessions)) {
		const responseFeedback = await getSummaryFeedbackForAnswersession({
			path: {
				answersession_id: Number(aid),
			},
		});

		if (responseFeedback.error) {
			showAlert = true;
			alertMessage = responseFeedback.error.detail;
			return;
		}
		feedbackPerAnswersession[aid] = responseFeedback.data;

		const milestoneGroupResponse = await getMilestonegroupsForSession({
			path: {
				answersession_id: Number(aid),
			},
		});

		if (milestoneGroupResponse.error) {
			showAlert = true;
			alertMessage = responseFeedback.error.detail;
			return;
		}
		milestongeGroups[aid] = milestoneGroupResponse.data;
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

function summarizeFeedback(feedback: Record<number, number>): number {
	let minscore = 1;
	for (const score of Object.values(feedback)) {
		if (score < minscore) {
			minscore = score;
		}
	}

	if (minscore < 0) {
		return -1;
	}
	if (minscore === 0) {
		return 0;
	}
	return 1;
}

const promise = setup();
</script>

{#await promise}
<div class = "flex justify-center items-center flex-row">
	<Spinner /> <p>{$_("childData.loadingMessage")}</p>
</div>
{:then}
<div>
    <Timeline>
		{#each sessionkeys as aid}
			{console.log("current session: ", aid, feedbackPerAnswersession[aid])}
			<TimelineItem classTime = "text-xl font-bold text-gray-700 dark:text-gray-400 " date = {formatDate(answerSessions[aid].created_at)}>
			<dev class = "flex flex-row text-gray-700 dark:text-gray-400 items-center ">
			{#if summarizeFeedback(feedbackPerAnswersession[aid]) === 1}
				<CheckCircleSolid color = "green" size="xl"/>
				<p class = "text-lg">{$_("childData.recommendOk")}</p>

			{:else if summarizeFeedback(feedbackPerAnswersession[aid]) === 0}
				<BellActiveSolid color = "orange"size="xl"/>
				<p class = "text-lg">{$_("childData.recommendWatch")}</p>

			{:else}
				<CircleMinusSolid color = "red" size="xl"/>
				<p class = "text-lg">{$_("childData.recommmendHelp")}</p>
			{/if}
			</dev>
			<Hr />
			<Accordion>
				{#each Object.entries(feedbackPerAnswersession[aid]) as [mid, score]}
				{console.log(" milestonegroup: ", mid, score)}
				<AccordionItem>
					<span slot="header">{milestongeGroups[aid][Number(mid)].text[$locale].title}</span>
					{#if Number(score)  > 0}
						<div class="flex flex-row items-center">
						<CheckCircleSolid color = "green" size="xl"/>
						<p class = "text-lg">{$_("childData.recommendOk")}</p>
						</div>
					{:else if Number(score) === 0}
						<div class="flex flex-row items-center">
						<BellActiveSolid color = "orange"size="xl"/>
						<p class = "text-lg">{$_("childData.recommendWatch")}</p>
						</div>

					{:else}
						<div class="flex flex-row items-center">
						<CircleMinusSolid color = "red" size="xl"/>
						<p class = "text-lg">{$_("childData.recommmendHelp")}</p>
						</div>
					{/if}
				</AccordionItem>
				{/each}
			</Accordion>
			</TimelineItem>
		{/each}
    </Timeline>
</div>
{:catch error}
<AlertMessage
    message = {`${alertMessage} ${error}`}
    title = {$_("childData.alertMessageTitle")}
/>
{/await}
