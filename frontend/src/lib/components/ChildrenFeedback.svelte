<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	type ValidationError,
	getDetailedFeedbackForMilestonegroup,
	getExpiredMilestoneAnswerSessions,
	getMilestonegroupsForSession,
	getSummaryFeedbackForAnswersession,
} from "$lib/client";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import {
	Accordion,
	AccordionItem,
	Button,
	Checkbox,
	Heading,
	Hr,
	Popover,
	Spinner,
	Timeline,
	TimelineItem,
} from "flowbite-svelte";

import {
	BellActiveSolid,
	CalendarWeekSolid,
	ChartLineUpOutline,
	CheckCircleSolid,
	ExclamationCircleSolid,
	UserSettingsOutline,
} from "flowbite-svelte-icons";

import {} from "flowbite-svelte-icons";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | ValidationError[] | undefined,
);
let answerSessions = $state({} as Record<number, MilestoneAnswerSessionPublic>);
let feedbackPerAnswersession = $state({} as Record<number, any>);
let milestoneGroups = $state({} as Record<number, any>);
let sessionkeys = $state([] as number[]);
let showHistory = $state(false);

const breadcrumbdata: any[] = [
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: $_("milestone.feedbackTitle"),
		onclick: () => {
			activeTabChildren.set("childrenFeedback");
		},
		symbol: ChartLineUpOutline,
	},
];

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
		milestoneGroups[Number(aid)] = milestoneGroupResponse.data;
	}
}

async function getDetailed(
	aid: number,
	mid: string,
): Promise<Record<string, number>> {
	const response = await getDetailedFeedbackForMilestonegroup({
		path: {
			answersession_id: aid,
			milestonegroup_id: Number(mid),
		},
	});

	if (response.error) {
		showAlert = true;
		alertMessage = response.error.detail;
		return {};
	}

	return response.data;
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

function summarizeFeedback(feedback: Record<number, number> | number): number {
	// get minimum score
	if (typeof feedback === "number") {
		return evaluate(feedback);
	}

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

{#snippet evaluation(value: Record<number, number> | number, with_text: boolean = true)}
	<div class="flex text-gray-700 dark:text-gray-400 items-center p-2 m-2">
		{#if summarizeFeedback(value) === 1}
			<CheckCircleSolid color = "green" size="xl"/>
			{#if with_text === true}
			<p >{$_("childData.recommendOk")}</p>
			{/if}

		{:else if summarizeFeedback(value) === 0}
			<BellActiveSolid color = "orange"size="xl"/>
			{#if with_text === true}
			<p >{$_("childData.recommendWatch")}</p>
			{/if}

		{:else}
			<ExclamationCircleSolid color = "red" size="xl"/>
			{#if with_text === true}
			<p>{$_("childData.recommmendHelp")}</p>
			{/if}
		{/if}
	</div>
{/snippet}

{#snippet detailedEvaluation(milestone: MilestonePublic, ms_score: number, )}
	<div class = "flex text-gray-700 dark:text-gray-400 items-center p-2 m-2">
		<p class="font-bold">{$_("milestone.milestone")} {milestone.text[$locale as string].title}: </p>
		{#if evaluate(ms_score) === 1}
			<CheckCircleSolid color = "green" size="xl"/>
		{:else if evaluate(ms_score) === 0}
			<BellActiveSolid color = "orange"size="xl"/>
			<Button id="b1">{$_("milestone.help")}</Button>
			<Popover title={$_("milestone.help")} triggeredBy="#b1"  trigger="click">
				{milestone.text[$locale as string].help}
			</Popover>
		{:else}
			<ExclamationCircleSolid color = "red" size="xl"/>
			<Button id="b2">{$_("milestone.help")}</Button>
			<Popover title={$_("milestone.help")} triggeredBy="#b2"  trigger="click">
				{milestone.text[$locale as string].help}
			</Popover>
		{/if}
	</div>
{/snippet}


<Breadcrumbs data={breadcrumbdata} />

{#if showAlert}
	<AlertMessage
		message = {alertMessage}
		title = {$_("childData.alertMessageTitle")}
	/>
{/if}

{#await promise}
	<div class = "flex justify-center items-center ">
		<Spinner /> <p>{$_("childData.loadingMessage")}</p>
	</div>
{:then}
	<Heading tag="h2" class = "text-gray-700 dark:text-gray-400 items-center p-2 m-2 pb-4">{$_("milestone.feedbackTitle")} </Heading>
	<Checkbox class= "pb-4 m-2 p-2"bind:checked={showHistory}>{$_("milestone.showHistory")}</Checkbox>

	<div class="m-2 mx-auto w-full pb-4 p-2">
		<Timeline order="horizontal">
			{#each sessionkeys as aid}

				{#if showHistory === true || aid === sessionkeys[sessionkeys.length -1]}
					<TimelineItem classTime = "text-lg font-bold text-gray-700 dark:text-gray-400 m-2 p-2" date = {formatDate(answerSessions[aid].created_at)}>
						<svelte:fragment slot="icon">
							<div class="flex items-center">
								<div class="flex z-10 justify-center items-center w-6 h-6 bg-primary-200 rounded-full ring-0 ring-white dark:bg-primary-900 sm:ring-8 dark:ring-gray-900 shrink-0">
								<CalendarWeekSolid class="w-4 h-4 text-primary-600 dark:text-primary-400" />
								</div>
								<div class="hidden sm:flex w-full bg-gray-200 h-0.5 dark:bg-gray-700" ></div>
							</div>
						</svelte:fragment>
						<dev class = "flex text-gray-700 dark:text-gray-400 items-center ">
						{@render evaluation(feedbackPerAnswersession[aid])}
						</dev>

						<Hr classHr= "mx-2"/>

						<Accordion class="p-2 m-2">
							{#each Object.entries(feedbackPerAnswersession[aid]) as [mid, score]}
								{#await getDetailed(aid, mid)}
									<Spinner /> <p>{$_("childData.loadingMessage")}</p>
								{:then detailed}
									<AccordionItem >
										<span slot="header" class = "text-gray-700 dark:text-gray-400 items-center" >
											<p class = "text-gray-700 dark:text-gray-400 font-bold" >
											{$_("milestone.milestoneGroup") }
											{milestoneGroups[aid][Number(mid)].text[$locale as string].title}</p>
											<Hr />
											{@render evaluation(score as number, true)}

										</span>

										<div class="flex-row justify-between">
											{#each Object.entries(detailed) as [ms_id, ms_score]}
												{@render detailedEvaluation(
													milestoneGroups[aid][Number(mid)].milestones.find((element: any) => element.id === Number(ms_id)),
													ms_score
												)}
											{/each}
										</div>
									</AccordionItem>
								{:catch error}
									<AlertMessage
										message = {`${alertMessage} ${error}`}
										title = {$_("childData.alertMessageTitle")}
									/>
								{/await}
							{/each}
						</Accordion>
					</TimelineItem>
				{/if}
			{/each}
		</Timeline>
	</div>
{:catch error}
	<AlertMessage
		message = {`${alertMessage} ${error}`}
		title = {$_("childData.alertMessageTitle")}
	/>
{/await}
