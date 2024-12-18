<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestoneGroupPublic,
	type MilestonePublic,
	type ValidationError,
	getDetailedFeedbackForAnswersession,
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
	Modal,
	Spinner,
	TabItem,
	Tabs,
} from "flowbite-svelte";
import {
	ArrowLeftOutline,
	ArrowRightOutline,
	BellActiveSolid,
	ChartLineUpOutline,
	CheckCircleSolid,
	CloseCircleSolid,
	ExclamationCircleSolid,
	EyeSolid,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

let showAlert = $state(false);
let alertMessage = $state(
	$_("childData.alertMessageError") as string | ValidationError[] | undefined,
);

let milestoneGroups = $state(
	{} as Record<number, Record<number, MilestoneGroupPublic>>,
);
let sessionkeys = $state([] as number[]);
let showHistory = $state(false);
let detailed = $state({}) as Record<number, any>;
let summary = $state({}) as Record<number, any>;
let answerSessions = $state({}) as Record<number, MilestoneAnswerSessionPublic>;
let showHelp = $state(false);
let showMoreInfo = $state(false);
const intervalSize = 4;
let currentSessionIndices = $state([0, intervalSize]);
let relevant_sessionkeys = $state([] as number[]);
const milestonePresentation = [
	{ icon: CheckCircleSolid, color: "green", text: $_("milestone.recommendOk") },
	{
		icon: EyeSolid,
		color: "green",
		text: $_("milestone.recommendOkWithCaveat"),
	},
	{
		icon: BellActiveSolid,
		color: "orange",
		text: $_("milestone.recommendWatch"),
	},
	{
		icon: ExclamationCircleSolid,
		color: "orange",
		text: $_("milestone.recommendWatchWithCaveat"),
	},
	{
		icon: CloseCircleSolid,
		color: "red",
		text: $_("milestone.recommmendHelp"),
	},
];
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

async function loadAnswersessions(): Promise<void> {
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
		.map((x) => Number(x))
		.reverse();
	const maxindex = Math.min(currentSessionIndices[1], sessionkeys.length);
	relevant_sessionkeys = sessionkeys.slice(currentSessionIndices[0], maxindex);
}

async function loadSummaryFeedback(relevant: number[]): Promise<void> {
	for (const aid of relevant) {
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

		milestoneGroups[Number(aid)] = {};
		for (const m of Object.values(milestoneGroupResponse.data)) {
			milestoneGroups[Number(aid)][m.id] = m;
		}

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

		summary[Number(aid)] = responseFeedback.data;
	}
}

async function loadDetailedFeedback(relevant: number[]): Promise<void> {
	for (const aid of relevant) {
		const response = await getDetailedFeedbackForAnswersession({
			path: {
				answersession_id: Number(aid),
			},
		});

		if (response.error) {
			showAlert = true;
			alertMessage = response.error.detail;
			return;
		}

		detailed[Number(aid)] = response.data;
	}
}

async function loadLast() {
	currentSessionIndices = [
		Math.max(currentSessionIndices[0] - intervalSize, 0),
		Math.max(currentSessionIndices[1] - intervalSize, intervalSize),
	];
	relevant_sessionkeys = sessionkeys.slice(
		currentSessionIndices[0],
		currentSessionIndices[1],
	);

	await loadSummaryFeedback(relevant_sessionkeys);
	await loadDetailedFeedback(relevant_sessionkeys);
}

async function loadNext() {
	currentSessionIndices = [
		Math.min(
			currentSessionIndices[0] + intervalSize,
			Math.max(sessionkeys.length - intervalSize, 0),
		),
		Math.min(currentSessionIndices[1] + intervalSize, sessionkeys.length),
	];
	relevant_sessionkeys = sessionkeys.slice(
		currentSessionIndices[0],
		currentSessionIndices[1],
	);

	await loadSummaryFeedback(relevant_sessionkeys);
	await loadDetailedFeedback(relevant_sessionkeys);
}

function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [
		dateObj.getDate(),
		dateObj.getMonth() + 1,
		dateObj.getFullYear(),
	].join("-");
}

function makeTitle(aid: number): string {
	return aid === sessionkeys[0]
		? $_("milestone.current")
		: formatDate(answerSessions[aid].created_at);
}

async function setup() {
	await loadAnswersessions();
	if (Object.keys(answerSessions).length === 0) {
		return;
	}
	await loadSummaryFeedback(relevant_sessionkeys);
	await loadDetailedFeedback(relevant_sessionkeys);
}

let promise = $state(setup());
</script>

{#snippet evaluation(aid: number, milestone_or_group: MilestonePublic | MilestoneGroupPublic | undefined, value: number, isMilestone: boolean, withText: boolean = false)}
	<div class="text-gray-700 dark:text-gray-400 space-x-2 space-y-4 p-2 m-2">
		{#if value === 2}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center">
				<CheckCircleSolid color = "green" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold " >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
				{#if withText}
				<p>{$_("milestone.recommendOk")}</p>
				{/if}
			</div>
		{:else if value === 1}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center">
				<EyeSolid color = "green" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold " >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
				{#if withText}
				<p>{$_("milestone.recommendOkWithCaveat")}</p>
				{/if}
			</div>
		{:else if value === 0}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center">
				<BellActiveSolid color = "orange" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold " >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
				{#if withText}
				<p>{$_("milestone.recommendWatch")}</p>
				{/if}
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal title={$_("milestone.help")} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else if value === -1}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center">
				<ExclamationCircleSolid color = "orange" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold " >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
				{#if withText}
				<p>{$_("milestone.recommendWatchWithCaveat")}</p>
				{/if}
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal title={$_("milestone.help")} bind:open={showHelp} dismissable={true} >
						{milestone_or_group?.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center">
				<CloseCircleSolid color = "red" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold " >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
				{#if withText}
				<p>{$_("milestone.recommmendHelp")}</p>
				{/if}
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>

					<Modal title={$_("milestone.help")} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{/if}
	</div>
{/snippet}


<Breadcrumbs data={breadcrumbdata} />

{#if showAlert}
	<AlertMessage
		message = {alertMessage}
		title = {$_("childData.alertMessageTitle")}
	/>
{:else}
	{#await promise}
		<div class = "flex justify-center items-center space-x-2">
			<Spinner /> <p>{$_("childData.loadingMessage")}</p>
		</div>
	{:then}

	<Heading tag="h2" class = "text-gray-700 dark:text-gray-400 items-center p-2 m-2 pb-4">{$_("milestone.feedbackTitle")} </Heading>

	<div class ="m-2 p-2 pb-4 ">
		<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-400">{$_("milestone.feedbackExplanation")}</p>

		<Button class = "m-2 p-2 pb-4 mb-4 items-center justify-center md:w-1/4" onclick = {() => {
			showMoreInfo = true;
		}}>{$_("milestone.moreInfoOnEval")}</Button>


		<Modal classHeader="flex justify-between items-center p-4 md:p-5 rounded-t-lg text-gray-700 dark:text-gray-400" title={$_("milestone.info")} bind:open={showMoreInfo} dismissable={true}>
			<p class ="text-gray-700 dark:text-gray-400">{$_("milestone.feedbackDetailsMilestoneGroup")}</p>
			<p class ="text-gray-700 dark:text-gray-400">{$_("milestone.feedbackDetailsMilestone")}</p>
		</Modal>

		<Accordion>
			<AccordionItem>
				<span slot="header" class="text-gray-700 dark:text-gray-400 flex items-center justify-center">
					<span class="font-bold">
						{$_("milestone.legend")}
					</span>
				</span>
				<div class="flex flex-col text-gray-700 dark:text-gray-400 items-start p-2 m-2 space-y-6 justify-center">
					{#each milestonePresentation as milestone}
						<div class="mx-2 px-2 w-full flex flex-row items-center">
							<svelte:component this={milestone.icon} color={milestone.color} size="xl" class="mx-2"/>
							<p>{milestone.text}</p>
						</div>
						<Hr classHr="mx-2 px-2 items-end w-full"/>
					{/each}
				</div>
			</AccordionItem>
		</Accordion>

		<Checkbox class= "pb-4 m-2 p-2 text-gray-700 dark:text-gray-400" bind:checked={showHistory}>{$_("milestone.showHistory")}</Checkbox>
		<Hr classHr= "mx-2"/>
	</div>

	<div class="m-2 p-2 pb-4 w-full">
		<Tabs tabStyle="underline" class="items-center flex flex-wrap">
			{#if showHistory === true}
				<Button size="md" type="button" class="md:w-16 md:h-8" on:click={() => {
					promise = loadLast();
				}}><ArrowLeftOutline class="w-4 h-4" /></Button>
			{/if}
			<div class="flex flex-col md:flex-row">
			{#each relevant_sessionkeys as aid}
				{#if showHistory === true || aid === sessionkeys[0]}
					<TabItem defaultClass="font-bold text-gray-700 dark:text-gray-400 m-2 p-2" title={makeTitle(aid)} open={aid === relevant_sessionkeys[0] }>
						<Accordion class="p-2 m-2">
							{#each Object.entries(summary[aid]) as [mid, score]}
								<AccordionItem >
									<span slot="header" class="text-gray-700 dark:text-gray-400 items-center flex justify-center space-x-2">
										{@render evaluation(aid, milestoneGroups[aid][Number(mid)], score as number, false, false)}
									</span>
									<div class="flex-row justify-between">
										{#each Object.entries(detailed[aid][mid]) as [ms_id, ms_score]}
											{@render evaluation(
												aid,
												milestoneGroups[aid][Number(mid)].milestones.find((element: any) =>
												{
													return element.id === Number(ms_id);
												}),
												Number(ms_score),
												true, true
											)}
											<Hr classHr="mx-2"/>
										{/each}
									</div>
								</AccordionItem>
							{/each}
						</Accordion>
					</TabItem>
				{/if}
			{/each}
			</div>
			{#if showHistory === true}
				<Button size="md" type="button" class="md:w-16 md:h-8" on:click={() => {
					promise = loadNext();
				}}><ArrowRightOutline class="w-4 h-4" /></Button>
			{/if}
		</Tabs>
	</div>
	{:catch error}
		<AlertMessage
			message = {`${alertMessage} ${error}`}
			title = {$_("childData.alertMessageTitle")}
		/>
	{/await}
{/if}
