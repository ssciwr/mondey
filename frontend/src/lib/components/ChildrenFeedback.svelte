<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type ValidationError,
	getExpiredMilestoneAnswerSessions,
	getSummaryFeedbackForAnswersession,
} from "$lib/client";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { user } from "$lib/stores/userStore.svelte";
import {
	Accordion,
	AccordionItem,
	Checkbox,
	Heading,
	Hr,
	Spinner,
	Timeline,
	TimelineItem,
} from "flowbite-svelte";
import {
	BellActiveSolid,
	CalendarWeekSolid,
	ChartLineUpOutline,
	CheckCircleSolid,
	CloseCircleSolid,
	ExclamationCircleSolid,
	EyeSolid,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | ValidationError[] | undefined,
);
let answerSessions = $state({} as Record<number, MilestoneAnswerSessionPublic>);
let summaryFeedbackPerAnswersession = $state({} as Record<number, any>);
let detailedFeedbackPerAnswersession = $state({} as Record<number, any>);
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
		summaryFeedbackPerAnswersession[Number(aid)] = responseFeedback.data;
	}
}

// async function getDetailed(
// 	aid: number,
// ): Promise<Record<string, Record<string, number>>> {
// 	const response = await getDetailedFeedbackForAnswersession({
// 		path: {
// 			answersession_id: aid,
// 		},
// 	});

// 	if (response.error) {
// 		showAlert = true;
// 		alertMessage = response.error.detail;
// 		return {};
// 	}

// 	return response.data;
// }

function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [
		dateObj.getDate(),
		dateObj.getMonth() + 1,
		dateObj.getFullYear(),
	].join("-");
}

// function evaluate(v: number): number {
// 	if (v < 0) {
// 		return -1;
// 	}
// 	if (v === 0) {
// 		return 0;
// 	}
// 	return 1;
// }

function summarizeFeedback(feedback: Record<number, number> | number): number {
	if (typeof feedback === "number") {
		return feedback;
	}

	const minscore = Math.min(...Object.values(feedback));

	return minscore;
}

const promise = setup();
</script>

{#snippet evaluation(value: Record<number, number> | number, with_text: boolean = true)}
	<div class="text-gray-700 dark:text-gray-400 items-center flex justify-center space-x-2 p-2 m-2">
		{#if summarizeFeedback(value) === 2}
			{#if with_text === true}
				<p >{$_("milestone.recommendOk")}</p>
			{/if}
			<CheckCircleSolid color = "green" size="xl"/>
		{:else if summarizeFeedback(value) === 1}
			{#if with_text === true}
				<p>{$_("milestone.recommendOkWithCaveat")}</p>
			{/if}
			<EyeSolid color = "green" size="xl"/>
		{:else if summarizeFeedback(value) === 0}
			{#if with_text === true}
				<p>{$_("milestone.recommendWatch")}</p>
			{/if}
			<BellActiveSolid color = "orange" size="xl"/>
		{:else if summarizeFeedback(value) === -1}
			{#if with_text === true}
				<p>{$_("milestone.recommendWatchWithCaveat")}</p>
			{/if}
			<ExclamationCircleSolid color = "orange" size="xl"/>
		{:else}
			{#if with_text === true}
				<p>{$_("milestone.recommmendHelp")}</p>
			{/if}
			<CloseCircleSolid color = "red" size="xl"/>
		{/if}
	</div>
{/snippet}
<!--
{#snippet detailedEvaluation(milestone: MilestonePublic, ms_score: number, )}
	<div class = "flex flex-col sm:flex-row text-gray-700 dark:text-gray-400 items-center justify-start space-x-2 p-2 m-2">
		{#if evaluate(ms_score) >=1 }
			<span class = "flex items-center flex-1 space-x-2">
			<p class="font-bold">{milestone.text[$locale as string].title} </p>
			<CheckCircleSolid color = "green" size="xl"/>
			</span>
		{:else if evaluate(ms_score) in [0, 1]}
			<span class ="flex items-center flex-1 space-x-2">
			<p class="font-bold">{milestone.text[$locale as string].title} </p>
			<BellActiveSolid color = "orange" size="xl"/>
			</span>
			<span class =  "ml-auto">
				<Button id="b1">{$_("milestone.help")}</Button>
				<Popover title={$_("milestone.help")} triggeredBy="#b1"  trigger="click">
					{milestone.text[$locale as string].help}
				</Popover>
			</span>
		{:else}
			<span class = "flex items-center flex-1 space-x-2">
				<p class="font-bold">{milestone.text[$locale as string].title} </p>
				<CloseCircleSolid color = "red" size="xl"/>
			</span>
			<span class = "ml-auto">
				<Button id="b2">{$_("milestone.help")}</Button>
				<Popover title={$_("milestone.help")} triggeredBy="#b2"  trigger="click">
					{milestone.text[$locale as string].help}
				</Popover>
			</span>
		{/if}
	</div>
{/snippet} -->


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

	<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-400">{$_("milestone.feedbackExplanation")}</p>

	<Checkbox class= "pb-4 m-2 p-2 text-gray-700 dark:text-gray-400" bind:checked={showHistory}>{$_("milestone.showHistory")}</Checkbox>
	<Hr classHr= "mx-2"/>

	<Accordion>
		<AccordionItem>
			<span slot="header" class = "text-gray-700 dark:text-gray-400 items-center flex justify-center space-x-2" >
				<span class = "font-bold" >
					{$_("milestone.legend")}
				</span>
			</span>
			<div class="flex flex-col sm:flex-row text-gray-700 dark:text-gray-400 items-start p-2 m-2 justify-center">
				<div class = "mx-2 px-2">
					<CheckCircleSolid color = "green" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendOk")}</p>
					<Hr classHr= "mx-2 items-end"/>
				</div>

				<div class = "mx-2 px-2">
					<EyeSolid color = "green" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendOkWithCaveat")}</p>
					<Hr classHr= "mx-2 items-end"/>
				</div>

				<div class = "mx-2 px-2">
					<BellActiveSolid color = "orange" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendWatch")}</p>
					<Hr classHr= "mx-2 items-end"/>
				</div>

				<div class = "mx-2 px-2">
					<ExclamationCircleSolid color = "orange" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendWatchWithCaveat")}</p>
					<Hr classHr= "mx-2 items-end"/>
				</div>

				<div class = "mx-2 px-2">
					<CloseCircleSolid color = "red" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommmendHelp")}</p>
					<Hr classHr= "mx-2 items-end"/>
				</div>

			</div>
		</AccordionItem>
	</Accordion>

	<div class="m-2 mx-auto w-full pb-4 p-2">
		<Timeline order="horizontal">
			{#each sessionkeys as aid}
				{#if showHistory === true || aid === sessionkeys[sessionkeys.length -1]}
					<TimelineItem classTime = "text-lg font-bold text-gray-700 dark:text-gray-400 m-2 p-2" date = {formatDate(answerSessions[aid].created_at)}>
						<svelte:fragment slot="icon">
							<div class="flex items-center">
								<div class="flex z-10 justify-center items-center w-6 h-6 bg-primary-200 rounded-full ring-0 ring-gray-200 dark:bg-primary-900 sm:ring-8 dark:ring-gray-400 shrink-0">
								<CalendarWeekSolid class="w-4 h-4 text-primary-600 dark:text-primary-400" />
								</div>
								<div class="hidden sm:flex w-full bg-gray-200 h-0.5 dark:bg-gray-700" ></div>
							</div>
						</svelte:fragment>

						<Hr classHr= "mx-2"/>
<!--
						<Accordion class="p-2 m-2">
							{#each Object.entries(summaryFeedbackPerAnswersession[aid]) as [mid, score]}
								{console.log('mid: ', mid, 'score: ', score)}
								{#await getDetailed(aid)}
									<Spinner /> <p>{$_("childData.loadingMessage")}</p>
								{:then detailed}
									<AccordionItem >
										<span slot="header" class = "text-gray-700 dark:text-gray-400 items-center flex justify-center space-x-2" >
											<span class = "text-gray-700 dark:text-gray-400 font-bold" >
											{milestoneGroups[aid][mid].text[$locale as string].title}
											</span>
											{@render evaluation( score as number, false)}
										</span>

										<div class="flex-row justify-between">
											{#each Object.entries(detailed) as [ms_id, ms_score]}
												{@render detailedEvaluation(
													milestoneGroups[aid][mid].milestones.find((element: any) => element.id === Number(ms_id)),
													ms_score
												)}
												<Hr classHr="mx-2"/>
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
						</Accordion> -->
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
