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
import { i18n } from "$lib/i18n.svelte";
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
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import AlertMessage from "./AlertMessage.svelte";

// data needed for displaying the page's content
let alertMessage = $state(
	i18n.tr.childData.alertMessageError as string | ValidationError[] | undefined,
);
let milestoneGroups = $state(
	{} as Record<number, Record<number, MilestoneGroupPublic>>,
);
let sessionkeys = $state([] as number[]);
let detailed = $state({}) as Record<number, any>; // detailed feedback for each milestone
let summary = $state({}) as Record<number, any>; // summary feedback for each milestonegroup
let answerSessions = $state({}) as Record<number, MilestoneAnswerSessionPublic>;

// helpers
const intervalSize = 6; // hardcoded number of answersessions to show at once
let currentSessionIndices = $state([0, intervalSize]); // lower and upper bond for currently shown indices
let relevant_sessionkeys = $state([] as number[]); // keys of the answersessions that are currently shown
let showMoreInfo = $state(false);
let showHelp = $state(false);
let showAlert = $state(false);

// data defining the legend for the feedback
let milestonePresentation = $state([
	{
		icon: CheckCircleSolid,
		text: i18n.tr.milestone.recommendOk,
		short: i18n.tr.milestone.recommendOkShort,
		class: "text-feedback-0 w-16",
		showExplanation: false,
	},
	{
		icon: BellActiveSolid,
		text: i18n.tr.milestone.recommendWatch,
		short: i18n.tr.milestone.recommendWatchShort,
		class: "text-feedback-1 w-16",
		showExplanation: false,
	},
	{
		icon: CloseCircleSolid,
		text: i18n.tr.milestone.recommmendHelp,
		short: i18n.tr.milestone.recommendHelpShort,
		class: "text-feedback-2 w-16 ",
		showExplanation: false,
	},
]);

// data defining where the breadcrumb elements should lead to
const breadcrumbdata: any[] = [
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: i18n.tr.milestone.feedbackTitle,
		onclick: () => {
			activeTabChildren.set("childrenFeedback");
		},
		symbol: ChartLineUpOutline,
	},
];

// functions needed for making decisions about page rendering and for doing some
// data preprocessing:
// TODO: for performance reasons, we could consider moving some of these functions to the backend,
// but this can be done once performance becomes a problem.

/**
 * Get the answersessions for the child we are concerned with from the database.
 * @summary Get the answersessions for the child we are concerned with from the database, set the sessionkeys as a sorted and reversed list of keys that we get from the response, and set the relevant_sessionkeys to be the interval of sessionkeys that we want to show.
 * @return {Promise<void>} nothing
 */
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

/**
 * Load the summary feedback for the relevant answersessions.
 * @param {number[]} relevant - Relevant session keys,i.e., those that are currently displayed
 * @return {Promise<void>} nothing
 */
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

/**
 * load the detailed feedback from the database for the child, i.e., the feedback on the milestones themselves, not just the groups.
 * @param {number[]} relevant - Relevant session keys,i.e., those that are currently displayed
 * @return {Promise<void>} nothing
 */
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

		let res = {} as Record<number, Record<number, number>>;

		// filter out the milestones that are not ideal and only show those
		for (const [mid, milestones] of Object.entries(response.data)) {
			res[Number(mid)] = {} as Record<number, number>;
			for (const [ms_id, ms_score] of Object.entries(milestones)) {
				if (ms_score <= 0) {
					res[Number(mid)][Number(ms_id)] = Number(ms_score);
				}
			}
		}

		detailed[Number(aid)] = res;
	}
}

/**
 * Load the last chunk of answersessions and feedbacks from the database. A chunk always has length 'intervalSize'.
 * @return {Promise<void>} nothing
 */
async function loadLast(): Promise<void> {
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

/**
 * Load the next chunk of answersessions and feedbacks from the database. A chunk always has length 'intervalSize'.
 * @return {Promise<void>} nothing
 */
async function loadNext(): Promise<void> {
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

/**
 * Generate a printable report from the feedback by concatenating all the feedbacks into a single formatted string.
 * @summary If the description is long, write your summary here. Otherwise, feel free to remove this.
 * @return {string} Report as a single string
 */
function generateReport(): string {
	let report = "";
	// add title
	report += `<h1>${i18n.tr.milestone.reportTitle}</h1>\n\n`;
	// add today's date
	report += `${i18n.tr.milestone.date}: ${new Date().toLocaleDateString()} \n\n`;

	// add name and age of child in the beginning
	report += `${i18n.tr.milestone.child}: ${currentChild.name}\n`;
	report += `${i18n.tr.milestone.born}: ${currentChild.month}/${currentChild.year} \n\n`;

	// iterate over all answersessions with aid:key
	for (let [aid, values] of Object.entries(summary)) {
		const min = Math.min(...(Object.values(values) as number[]));
		report += `<h2>${i18n.tr.milestone.timeperiod}: ${makeTitle(Number(aid))}</h2> \n`;
		report += `<strong>${i18n.tr.milestone.summaryScore}:</strong> ${min === 1 ? i18n.tr.milestone.recommendOk : min === 0 ? i18n.tr.milestone.recommendWatch : min === -1 ? i18n.tr.milestone.recommmendHelp : i18n.tr.milestone.notEnoughDataYet} \n\n`;

		for (let [mid, score] of Object.entries(values)) {
			// mid : score
			report += `<h3>  ${milestoneGroups[aid][Number(mid)].text[i18n.locale].title}</h3>`;
			report += `    ${score === 1 ? i18n.tr.milestone.recommendOk : score === 0 ? i18n.tr.milestone.recommendWatch : score === -1 ? i18n.tr.milestone.recommmendHelp : i18n.tr.milestone.notEnoughDataYet} \n\n`;

			for (let [ms_id, ms_score] of Object.entries(detailed[aid][mid])) {
				// ms_id : ms_score
				report += `    <strong>${
					milestoneGroups[aid][Number(mid)].milestones.find((element: any) => {
						return element.id === Number(ms_id);
					}).text[i18n.locale].title
				}:</strong>`;
				report += ` ${ms_score === 1 ? i18n.tr.milestone.recommendOkShort : ms_score === 0 ? i18n.tr.milestone.recommendWatchShort : ms_score === -1 ? i18n.tr.milestone.recommendHelpShort : i18n.tr.milestone.notEnoughDataYet} \n`;
			}
		}

		report += "\n";
	}

	return report;
}

/**
 * Print the report generated by the generateReport function, which is called internally.
 * @return {void} Nothing
 */
function printReport(): void {
	const report = generateReport();
	const printWindow = window.open("", "", "height=600,width=800");
	if (printWindow === null) {
		return;
	}
	printWindow.document.write(`<pre>${report}</pre>`);
	printWindow.document.close();
	printWindow.print();
}

/**
 * Function for formatting a given datetime string into a more readable format.
 * @param {string} date - The date to format.
 * @return {string} The formatted date: day - month - year
 */
function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [
		dateObj.getDate(),
		dateObj.getMonth() + 1,
		dateObj.getFullYear(),
	].join("-");
}

/**
 * Create a title for the answersession, using the created_at field of the answersession data.
 * @param {number} aid - The id of the answersession to create a title from.
 * @return {ReturnValueDataTypeHere} Brief description of the returning value here.
 */
function makeTitle(aid: number): string {
	return aid === sessionkeys[0]
		? i18n.tr.milestone.current
		: formatDate(answerSessions[aid].created_at);
}

/**
 * Load the data and get everything ready to render the page
 * @return { Promise<void>} nothign
 */
async function setup(): Promise<void> {
	await loadAnswersessions();
	if (Object.keys(answerSessions).length === 0) {
		return;
	}
	await loadSummaryFeedback(relevant_sessionkeys);
	await loadDetailedFeedback(relevant_sessionkeys);
}

// create a promise that will be resolved when the data is loaded
let promise = $state(setup());
</script>

<!--Snippet that shows the evaluation for the whole answersession: uses the minimum of the milestonegroup currently-->
{#snippet summaryEvaluation(aid: number)}
	<div class="flex flex-col md:flex-row items-center justify-center w-full m-2 p-2 text-gray-700 dark:text-gray-200">
		{#if Math.min(...(Object.values(summary[aid]) as number[])) === 1}
			<CheckCircleSolid  size="xl" class="transform scale-150 text-feedback-0 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center">{i18n.tr.milestone.summaryScore}</span>
			{i18n.tr.milestone.recommendOk}
		{:else if Math.min(...(Object.values(summary[aid]) as number[])) === 0}
			<BellActiveSolid size="xl" class="transform scale-150 text-feedback-1 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center">{i18n.tr.milestone.summaryScore}</span>
			{i18n.tr.milestone.recommendWatch}
		{:else if Math.min(...(Object.values(summary[aid]) as number[])) === -1}
			<CloseCircleSolid size="xl" class="text-feedback-2 mr-2 pr-2"/>
			<span class="font-bold mx-2 px-2 items-center justify-center"> {i18n.tr.milestone.summaryScore}</span>
			{i18n.tr.milestone.recommmendHelp}
		{:else}
			<CloseCircleSolid size="xl" color = "gray" />
			<span class="font-bold mx-2 px-2 items-center justify-center">{i18n.tr.milestone.summaryScore}</span>
			{i18n.tr.milestone.notEnoughDataYet}
		{/if}
	</div>
<Hr classHr="mx-2"/>
{/snippet}

<!--Snippet defining how the evaluation for each milestonegroup is shown. 'grade' is the evaluation we get from the backend-->
{#snippet evaluation( milestone_or_group: MilestonePublic | MilestoneGroupPublic | undefined, grade: number, isMilestone: boolean,)}
	<div class={`rounded-lg space-x-2 space-y-4 p-2 m-2 flex flex-col ${(grade === 0 || grade === -1) && isMilestone=== true ? "bg-feedback-background-0" : ""}`}>
		{#if grade === 1}
			<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<CheckCircleSolid  size="xl" class="text-feedback-0"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-200": ""}`} >
					{milestone_or_group?.text[i18n.locale].title}
				</span>
				<Hr class="mx-2"/>
			</div>
		{:else if grade === 0}
			<div class="flex flex-col md:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<BellActiveSolid size="xl" class="text-feedback-1"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-700": ""}`} >
					{milestone_or_group?.text[i18n.locale].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4 " >
					<Button class = "bg-gray-500 dark:bg-gray-500 hover:bg-gray-400 dark:hover:bg-gray-400 focus-within:ring-gray-40" id="b1" onclick={()=>{
						showHelp= true;
					}}>{i18n.tr.milestone.help}</Button>
					<Modal class = "m-2 p-2" title={i18n.tr.milestone.help} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[i18n.locale].help}
					</Modal>
				</span>
			{/if}
		{:else if grade === -1}
			<div class="flex flex-col md:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
				<CloseCircleSolid size="xl" class="text-feedback-2"/>
				<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-700" : ""}`} >
					{milestone_or_group?.text[i18n.locale].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			{#if isMilestone}
				<span class =  "ml-auto mt-4">
					<Button class = "bg-gray-500 dark:bg-gray-500 hover:bg-gray-400 dark:hover:bg-gray-400 focus-within:ring-gray-40" id="b1" onclick={()=>{
						showHelp= true;
					}}>{i18n.tr.milestone.help}</Button>
					<Modal class = "m-2 p-2" title={i18n.tr.milestone.help} bind:open={showHelp} dismissable={true}>
						{milestone_or_group?.text[i18n.locale].help}
					</Modal>
				</span>
			{/if}
		{:else }
		<div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 items-center m-2 p-2">
			<CloseCircleSolid color = "gray" size="xl"/>
			<span class = {`font-bold ${isMilestone? "text-gray-700 dark:text-gray-700": ""}`} >
				{milestone_or_group?.text[i18n.locale].title}
			</span>
			<Hr class="mx-2"/>
		</div>

		{/if}
	</div>
{/snippet}

<!-- Legend -->
<!-- A grid view with symbol | shorthand(bold) | explanation  on larger screens and | symbol | shorthand on smaller screens -->
{#snippet legend }
	<div class="m-2 w-full mb-4 text-gray-700 dark:text-gray-200 mb-4 pb-4">
		<p class="mb-4 pb-4">{i18n.tr.milestone.feedbackExplanation}</p>
		<div class ="grid grid-cols-[auto_1fr_2fr] gap-4">
			{#each milestonePresentation as milestone}
				<div class="flex justify-center">
					<svelte:component this={milestone.icon} size="xl" class={milestone.class} />
				</div>
				<span class="font-bold">{milestone.short}</span>
				<span class="hidden sm:block">{milestone.text}</span>
			<div class="col-span-3">
				<Hr classHr="w-full my-2" />
			</div>
			{/each}
		</div>
	</div>
{/snippet}

<!-- Central part of the page with a buttton that enables the explanation modal for the feedback, and a heading that tells people what they can do next -->
{#snippet explanationModal}
	<div class="text-gray-700 dark:text-gray-200 flex flex-cols justify-between m-2 mb-4 pb-4">
		<Heading tag="h4" class="text-gray-700 dark:text-gray-200">{i18n.tr.milestone.selectFeedback}</Heading>

		<Button class="bg-gray-500 dark:bg-gray-500 hover:bg-gray-400 focus-within:ring-gray-40 font-bold" size="md" type="button" on:click={() => {
			showMoreInfo = true;
		}}
		>{i18n.tr.milestone.moreInfoOnEval}</Button>
	</div>

	<!-- Modal that shows the explanation of the feedback when the above button is clicked			 -->
	<Modal class = "m-2 p-2" classHeader="flex justify-between items-center p-4 md:p-5 rounded-t-lg text-gray-700 dark:text-gray-200" title={i18n.tr.milestone.info} bind:open={showMoreInfo} dismissable={true}>
		<p class ="text-gray-700 dark:text-gray-200 font-medium ">{i18n.tr.milestone.feedbackExplanationDetailed}</p>
		<p class ="text-gray-700 dark:text-gray-200 font-medium ">{i18n.tr.milestone.feedbackDetailsMilestone}</p>
		<p class ="text-gray-700 dark:text-gray-200 font-medium " >{i18n.tr.milestone.feedbackDetailsEval}</p>
	</Modal>
{/snippet}

<!-- The main element of the page: Accordion display of milestone group feedback with detailed feedback for 
 suboptimal milestones available on click-->
{#snippet milestoneGroupsEval(aid)}
	<Accordion class="p-2 m-2 grid grid-cols-1 md:grid-cols-3 gap-4">
		{#each Object.entries(summary[aid]) as [mid, score]}
			<div class="flex flex-col">
				<AccordionItem activeClass="flex flex-col m-2 rounded-xl text-white dark:text-white bg-primary-700 dark:bg-primary-700 hover:bg-primary-600 dark:hover:bg-primary-600 items-center justify-between w-full font-medium text-left" inactiveClass="flex flex-col rounded-xl text-white dark:text-white bg-primary-800 dark:bg-primary-800 hover:bg-primary-700 dark:hover:bg-primary-700 items-center justify-between w-full font-medium text-left m-2">
					<span slot="header" class="items-center flex justify-center space-x-2">
						{@render evaluation(milestoneGroups[aid][Number(mid)], score as number, false)}
					</span>
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
				</AccordionItem>
			</div>
		{/each}
	</Accordion>
{/snippet}

<!--topmost navigation element that lets us go back to children overview and child data-->
<Breadcrumbs data={breadcrumbdata} />

{#if showAlert}
	<AlertMessage
		message = {`${alertMessage}`}
		title = {i18n.tr.childData.alertMessageTitle}
		onclick={() => {
			showAlert = false;
		}}
	/>
{:else}
	{#await promise}
		<!-- show a loading symbol if the data is not yet available-->
		<div class = "flex justify-center items-center space-x-2">
			<Spinner /> <p>{i18n.tr.childData.loadingMessage}</p>
		</div>
	{:then}
		<Heading tag="h2" class = "text-gray-700 dark:text-gray-200 items-center p-2 m-2 pb-4">{i18n.tr.milestone.feedbackTitle} </Heading>

		{@render legend}

		{@render explanationModal}

		<!--Main tabs component that displays the feedback for the milestones and milestonegroups -->
		<Tabs defaultClass="m-2 p-2 pb-4 items-center flex flex-wrap justify-between w-full text-gray-700 dark:text-gray-200">
			<div class="flex flex-col md:flex-row justify-between">
				{#if relevant_sessionkeys.length=== 0}
					<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-200">{i18n.tr.milestone.noFeedback}</p>
				{:else}
					{#each relevant_sessionkeys as aid}
						<TabItem defaultClass="font-bold m-2 p-2" title={makeTitle(aid)} open={aid === relevant_sessionkeys[0] }>

							{@render summaryEvaluation(aid)}

							{@render milestoneGroupsEval(aid)}
						</TabItem>
					{/each}
				{/if}
			</div>
		</Tabs>

		<!--Button to print the report out into pdf or physical copy-->
		<div class="flex items-center justify-center w-full m-2 p-2 mb-4 pb-4">
			<Button class="md:w-64 md:h-8  m-2 p-2 bg-gray-500 dark:bg-gray-500 hover:bg-gray-400 focus-within:ring-gray-40" onclick={printReport}>{i18n.tr.milestone.printReport}</Button>
		</div>
	{:catch error}
		<AlertMessage
			message = {`${alertMessage} ${error}`}
			title = {i18n.tr.childData.alertMessageTitle}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/await}
{/if}
