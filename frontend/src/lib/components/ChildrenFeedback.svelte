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
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
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
let showHistory = $state(true);
let detailed = $state({}) as Record<number, any>;
let summary = $state({}) as Record<number, any>;
let answerSessions = $state({}) as Record<number, MilestoneAnswerSessionPublic>;
let showHelp = $state(false);
let showMoreInfo = $state(false);
const intervalSize = 4;
let currentSessionIndices = $state([0, intervalSize]);
let relevant_sessionkeys = $state([] as number[]);
let milestonePresentation = $state([
	{
		icon: CheckCircleSolid,
		text: $_("milestone.recommendOk"),
		short: $_("milestone.recommendOkShort"),
		class: "text-feedback-0 w-16",
		showExplanation: false,
	},
	{
		icon: ExclamationCircleSolid,
		text: $_("milestone.recommendWatch"),
		short: $_("milestone.recommendWatchShort"),
		class: "text-feedback-1 w-16",
		showExplanation: false,
	},
	{
		icon: CloseCircleSolid,
		text: $_("milestone.recommmendHelp"),
		short: $_("milestone.recommendHelpShort"),
		class: "text-feedback-2 w-16 ",
		showExplanation: false,
	},
]);
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

function scrollToBottom() {
	window.scrollTo({
		top: document.body.scrollHeight,
		behavior: "smooth",
	});
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

{#snippet summaryEvaluation(aid: number)}
	<div class="flex flex-col md:flex-row items-center justify-center w-full m-2 p-2 text-gray-700 dark:text-gray-400">
		{#if Math.min(...(Object.values(summary[aid]) as number[])) === 1}
			<CheckCircleSolid  size="xl" class="text-feedback-0 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center">{$_("milestone.summaryScore")}</span>
			{$_("milestone.recommendOk")}
		{:else if Math.min(...(Object.values(summary[aid]) as number[])) === 0}
			<BellActiveSolid size="xl" class="text-feedback-1 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center">{$_("milestone.summaryScore")}</span>
			{$_("milestone.recommendWatch")}
		{:else if Math.min(...(Object.values(summary[aid]) as number[])) === -1}
			<CloseCircleSolid size="xl" class="text-feedback-2 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center"> {$_("milestone.summaryScore")}</span>
			{$_("milestone.recommmendHelp")}
		{:else}
			<CloseCircleSolid size="xl" color = "gray" />
			<span class="font-bold mx-2 px-2 items-center justify-center">{$_("milestone.summaryScore")}</span>
			{$_("milestone.notEnoughDataYet")}
		{/if}
	</div>
<Hr classHr="mx-2"/>

{/snippet}


{#snippet evaluation( milestone_or_group: MilestonePublic | MilestoneGroupPublic | undefined, value: number, isMilestone: boolean,)}
	<div class=" space-x-2 space-y-4 p-2 m-2 flex flex-col">
		{#if value === 1}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<CheckCircleSolid  size="xl" class="text-feedback-0"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-400": ""}`} >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
		{:else if value === 0}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<BellActiveSolid size="xl" class="text-feedback-1"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-400": ""}`} >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal class = "m-2 p-2" title={$_("milestone.help")} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else if value === -1}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<CloseCircleSolid size="xl" class="text-feedback-2"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-400": ""}`} >
					{milestone_or_group?.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>

					<Modal class = "m-2 p-2" title={$_("milestone.help")} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else }
		<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
			<CloseCircleSolid color = "gray" size="xl"/>
			<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-400": ""}`} >
				{milestone_or_group?.text[$locale as string].title}
			</span>
			<Hr class="mx-2"/>
		</div>

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
			<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-400 font-medium text-sm md:text-md">{$_("milestone.feedbackExplanation")}</p>

			<Modal class = "m-2 p-2" classHeader="flex justify-between items-center p-4 md:p-5 rounded-t-lg text-gray-700 dark:text-gray-400" title={$_("milestone.info")} bind:open={showMoreInfo} dismissable={true}>
				<p class ="text-gray-700 dark:text-gray-400 font-medium text-sm md:text-md">{$_("milestone.feedbackExplanationDetailed")}</p>
				<p class ="text-gray-700 dark:text-gray-400 font-medium text-sm md:text-md">{$_("milestone.feedbackDetailsMilestoneGroup")}</p>
				<p class ="text-gray-700 dark:text-gray-400 font-medium text-sm md:text-md" >{$_("milestone.feedbackDetailsMilestone")}</p>
			</Modal>

			<Accordion class="p-2 m-2">
				<AccordionItem>
				<span class="text-gray-700 dark:text-gray-400" slot="header">{$_("milestone.legend")}</span>
				<Table striped={false}>
					<TableBody tableBodyClass="divide-y">
						{#each milestonePresentation as milestone}
							<TableBodyRow class="text-gray-700 dark:text-gray-400 flex flex-col md:flex-row font-medium text-sm md:text-md items-center justify-center m-2 p-2">

								<TableBodyCell class="flex flex-col w-32 justify-center"><svelte:component this={milestone.icon}  size="xl" class={milestone.class} /></TableBodyCell>

								<TableBodyCell class="flex flex-col font-bold justify-center mr-auto pr-auto">{milestone.short}</TableBodyCell>

								<TableBodyCell class="flex flex-col justify-end w-32"><Button class="m-2 p-2 w-full justify-center" onclick={() => {milestone.showExplanation=true;}}>{$_("milestone.moreInfoOnLegend")}</Button></TableBodyCell>
							</TableBodyRow>
							<Modal class = "m-2 p-2" classHeader="flex justify-between items-center p-4 md:p-5 rounded-t-lg text-gray-700 dark:text-gray-400" bind:open={milestone.showExplanation} dismissable={true} title={milestone.short}>
								{milestone.text}
							</Modal>
						{/each}
					</TableBody>
				</Table>

			</AccordionItem>
			</Accordion>

			<div class="flex items-center justify-center w-full m-2 p-2">
				<Button class = "m-2 p-2 pb-4 mb-4 items-center justify-center md:w-1/6" onclick = {() => {
					showMoreInfo = true;
				}}>{$_("milestone.moreInfoOnEval")}
				</Button>
			</div>
		</div>

		<Hr classHr= "w-full mx-2"/>

		<div class ="m-2 p-2 pb-4 ">

			<p class = "justify-center font-bold m-2 p-2 text-gray-700 dark:text-gray-400">{$_("milestone.selectFeedback")}</p>

			<Checkbox class= "pb-4 m-2 p-2 text-gray-700 dark:text-gray-400" bind:checked={showHistory} >{$_("milestone.showHistory")}</Checkbox>

			<Hr classHr= "mx-2"/>
		</div>

		<Tabs defaultClass="m-2 p-2 pb-4 items-center flex flex-wrap justify-between w-full text-gray-700 dark:text-gray-400">
			{#if showHistory === true}
				<Button size="md" type="button" class="md:w-16 md:h-8" on:click={() => {
					promise = loadLast();
					scrollToBottom();
				}}><ArrowLeftOutline class="w-4 h-4" /></Button>
			{/if}
			<div class="flex flex-col md:flex-row justify-between">
				{#if relevant_sessionkeys.length=== 0}
					<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-400">{$_("milestone.noFeedback")}</p>
				{:else}
					{#each relevant_sessionkeys as aid}
						{#if showHistory === true || aid === sessionkeys[0]}
							<TabItem defaultClass="font-bold m-2 p-2" title={makeTitle(aid)} open={aid === relevant_sessionkeys[0] }>

								{@render summaryEvaluation(aid)}

								<Accordion class="p-2 m-2 grid grid-cols-1 md:grid-cols-3 gap-4">
									{#each Object.entries(summary[aid]) as [mid, score]}
										<div class="flex flex-col">
										<AccordionItem activeClass="flex flex-col m-2 rounded-xl text-white dark:text-white bg-primary-700 dark:bg-primary-700 hover:bg-primary-600 dark:hover:bg-primary-600 items-center justify-between w-full font-medium text-left" inactiveClass="flex flex-col rounded-xl text-white dark:text-white bg-primary-800 dark:bg-primary-800 hover:bg-primary-700 dark:hover:bg-primary-700  items-center justify-between w-full font-medium text-left m-2">
											<span slot="header" class="items-center flex justify-center space-x-2">
												{@render evaluation(milestoneGroups[aid][Number(mid)], score as number, false)}
											</span>
											<div class="flex-row justify-between">
												{#each Object.entries(detailed[aid][mid]) as [ms_id, ms_score]}
													{@render evaluation(
														milestoneGroups[aid][Number(mid)].milestones.find((element: any) =>
														{
															return element.id === Number(ms_id);
														}),
														Number(ms_score),
														true
													)}
													<Hr classHr="mx-2"/>
												{/each}
											</div>
										</AccordionItem>
										</div>
									{/each}
								</Accordion>
							</TabItem>
						{/if}
					{/each}
				{/if}
			</div>

			{#if showHistory === true}
				<Button size="md" type="button" class="md:w-16 md:h-8" on:click={() => {
					promise = loadNext();
					scrollToBottom();
				}}><ArrowRightOutline class="w-4 h-4" /></Button>
			{/if}
		</Tabs>

		<div class="flex items-center justify-center w-full m-2 p-2 mb-4 pb-4">
			<Button class="md:w-64 md:h-8  m-2 p-2" onclick={() => window.print()}>{$_("milestone.printPage")}</Button>
		</div>
	{:catch error}
		<AlertMessage
			message = {`${alertMessage} ${error}`}
			title = {$_("childData.alertMessageTitle")}
		/>
	{/await}
{/if}
