<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type ValidationError,
	getDetailedFeedbackForMilestonegroup,
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
	$_("childData.alertMessageError") as string | ValidationError[] | undefined,
);
let answerSessions = $state({} as Record<number, MilestoneAnswerSessionPublic>);
let feedbackPerAnswersession = $state({} as Record<number, any>);
let milestongeGroups = $state({} as Record<number, any>);
let sessionkeys = $state([] as number[]);
let detailed = $state({} as Record<string, number>);

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
		feedbackPerAnswersession[Number(aid)] = responseFeedback.data;

		const milestoneGroupResponse = await getMilestonegroupsForSession({
			path: {
				answersession_id: Number(aid),
			},
		});

		if (milestoneGroupResponse.error) {
			showAlert = true;
			alertMessage = milestoneGroupResponse.error.detail;
			return;
		}
		milestongeGroups[Number(aid)] = milestoneGroupResponse.data;
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

function evaluate(v: number): number {
	if (v < 0) {
		return -1;
	}
	if (v === 0) {
		return 0;
	}
	return 1;
}

function summarizeFeedback(feedback: Record<number, number>): number {
	let minscore = 1;
	for (const score of Object.values(feedback)) {
		if (score < minscore) {
			minscore = score;
		}
	}
	return evaluate(minscore);
}

const promise = setup();
</script>

{#snippet evaluation(value: Record<number, number>, with_text: boolean = true)}
	{#if summarizeFeedback(value) === 1}
		<CheckCircleSolid color = "green" size="xl"/>
		{#if with_text === true}
		<p class = "text-lg">{$_("childData.recommendOk")}</p>
		{/if}

	{:else if summarizeFeedback(value) === 0}
		<BellActiveSolid color = "orange"size="xl"/>
		{#if with_text === true}
		<p class = "text-lg">{$_("childData.recommendWatch")}</p>
		{/if}

	{:else}
		<CircleMinusSolid color = "red" size="xl"/>
		{#if with_text === true}
		<p class = "text-lg">{$_("childData.recommmendHelp")}</p>
		{/if}
	{/if}
{/snippet}


{#await promise}
<div class = "flex justify-center items-center flex-row">
	<Spinner /> <p>{$_("childData.loadingMessage")}</p>
</div>
{:then}
<div>
    <Timeline>
		{#each sessionkeys as aid}
			<TimelineItem classTime = "text-xl font-bold text-gray-700 dark:text-gray-400 " date = {formatDate(answerSessions[aid].created_at)}>
			<dev class = "flex flex-row text-gray-700 dark:text-gray-400 items-center ">
			{@render evaluation(feedbackPerAnswersession[aid])}
			</dev>
			<Hr />
			<Accordion>
				{#each Object.entries(feedbackPerAnswersession[aid]) as [mid, score]}
				<AccordionItem on:click = {async () => {
					console.log("clicked on accordion item");
					const response = await getDetailedFeedbackForMilestonegroup({
						path: {
							answersession_id: aid,
        					milestonegroup_id: Number(mid)
						}
					});
					if (response.error) {
						showAlert = true;
						alertMessage = response.error.detail;
						return;
					}
					console.log("detailed feedback: ", response.data);
					detailed = response.data;

				}}>
					<span slot="header">{milestongeGroups[aid][Number(mid)].text[$locale as string].title}</span>
					{@render evaluation(score as Record<number, number>, false)}
					{#each Object.entries(detailed) as [ms_id, ms_score]}
						<p>{milestongeGroups[aid][Number(mid)].milestones[ms_id].text[$locale as string].title}</p>
						{#if evaluate(ms_score) === 1}
							<CheckCircleSolid color = "green" size="xl"/>
						{:else if evaluate(ms_score) === 0}
							<BellActiveSolid color = "orange"size="xl"/>
						{:else}
							<CircleMinusSolid color = "red" size="xl"/>
						{/if}
					{/each}
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
