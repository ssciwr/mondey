<svelte:options runes={true} />
<script lang="ts">
import { goto } from "$app/navigation";
import {
	type GetSummaryFeedbackForAnswersessionResponse,
	type MilestoneAnswerSessionPublic,
	type MilestoneGroupPublic,
	type MilestonePublic,
	type ValidationError,
	getCompletedMilestoneAnswerSessions,
	getDetailedFeedbackForAnswersession,
	getMilestonegroupsForSession,
	getSummaryFeedbackForAnswersession,
} from "$lib/client";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Accordion,
	AccordionItem,
	Button,
	Heading,
	Hr,
	Modal,
	Spinner,
	TabItem,
	Tabs,
} from "flowbite-svelte";
import {
	ChartLineUpOutline,
	CheckCircleSolid,
	CloseCircleSolid,
	ExclamationCircleSolid,
	GridPlusSolid,
	QuestionCircleSolid,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

// data needed for displaying the page's content
let alertMessage = $state(
	i18n.tr.childData.alertMessageError as string | ValidationError[] | undefined,
);
let milestoneGroups = $state(
	{} as Record<number, Record<number, MilestoneGroupPublic>>,
);
let detailed = $state({}) as Record<number, any>; // detailed feedback for each milestone
let summary = $state({}) as Record<number, any>; // summary feedback for each milestonegroup
let answerSessions = $state({}) as Record<number, MilestoneAnswerSessionPublic>;

// helpers
const breakpoints = {
	sm: 640,
	md: 768,
	lg: 1024,
	xl: 1280,
	"2xl": 1536,
};
let windowWidth = $state(0);

// adjustment of displayed data based on current window width
onMount(() => {
	// Set initial width
	windowWidth = window.innerWidth;

	// Add event listener
	const handleResize = () => {
		windowWidth = window.innerWidth;
	};

	window.addEventListener("resize", handleResize);

	// Clean up event listener when component unmounts
	return () => {
		window.removeEventListener("resize", handleResize);
	};
});

let numShownAnswersessions = $derived.by(() => {
	if (windowWidth >= breakpoints["2xl"]) {
		return 10;
	}
	if (windowWidth >= breakpoints.xl) {
		return 8;
	}
	if (windowWidth >= breakpoints.lg) {
		return 6;
	}
	if (windowWidth >= breakpoints.md) {
		return 4;
	}
	if (windowWidth >= breakpoints.sm) {
		return 3;
	}
	return 2;
});

let relevant_sessionkeys = $derived.by(() => {
	const upper_limit = Math.min(
		numShownAnswersessions,
		Object.keys(answerSessions).length,
	);
	return Object.keys(answerSessions)
		.sort()
		.map((x) => Number(x))
		.reverse()
		.slice(0, upper_limit);
}); // record the keys of the answersessions that are currently displayed

// other helper state variables
let showMoreInfo = $state(false);
let showHelp = $state(false);

// promises to load the data and steer page loading
let sessionPromise = $state(loadAnswersessions());

// data defining the legend for the feedback
let milestonePresentation = [
	{
		icon: CheckCircleSolid,
		text: i18n.tr.milestone.recommendOk,
		short: i18n.tr.milestone.recommendOkShort,
		class: "text-feedback-0 w-16",
		showExplanation: false,
	},
	{
		icon: QuestionCircleSolid,
		text: i18n.tr.milestone.recommendWatch,
		short: i18n.tr.milestone.recommendWatchShort,
		class: "text-feedback-1 w-16",
		showExplanation: false,
	},
	{
		icon: ExclamationCircleSolid,
		text: i18n.tr.milestone.recommendHelp,
		short: i18n.tr.milestone.recommendHelpShort,
		class: "text-feedback-2 w-16 ",
		showExplanation: false,
	},
];

// data defining where the breadcrumb elements should lead to
const breadcrumbdata: any[] = [
	{
		label: i18n.tr.childData.overviewLabel,
		onclick: () => {
			goto("/userLand/children");
		},
		symbol: GridPlusSolid,
	},
	{
		label: currentChild.name,
		onclick: () => {
			goto("/userLand/children/registration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: i18n.tr.milestone.feedbackTitle,
		onclick: () => {
			goto("/userLand/children/feedback");
		},
		symbol: ChartLineUpOutline,
	},
];

// functions needed for making decisions about page rendering and for doing some
// data preprocessing:
/**
 * Get the answersessions for the child we are concerned with from the database.
 * @summary Get the answersessions for the child we are concerned with from the database, set the sessionkeys as a sorted and reversed list of keys that we get from the response, and set the relevant_sessionkeys to be the interval of sessionkeys that we want to show.
 * @return {Promise<void>} nothing
 */
async function loadAnswersessions(): Promise<void> {
	if (!user.data) {
		await user.load();
	}
	await currentChild.load_data();
	if (currentChild.id === null || user.id === null) {
		await goto("/userLand/children");
		return;
	}

	// load all answersessions initially
	const responseAnswerSessions = await getCompletedMilestoneAnswerSessions({
		path: { child_id: currentChild.id },
	});

	if (responseAnswerSessions.error) {
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			responseAnswerSessions.error.detail,
			true,
			false,
		);
		return;
	}
	answerSessions = responseAnswerSessions.data;
	if (Object.keys(answerSessions).length > 0) {
		await loadData(relevant_sessionkeys[0]);
	}
}

/**
 * Load the summary feedback for the relevant answersessions.
 * @param {number} requested_answersession - Answersessionkey for which we want to load the summary feedback
 * @return {Promise<Promise< GetSummaryFeedbackForAnswersessionResponse | null>>} The summary feedback for the requested answersession
 */
async function loadSummaryFeedbackFor(
	requested_answersession: number,
): Promise<GetSummaryFeedbackForAnswersessionResponse | null> {
	if (
		requested_answersession in summary &&
		requested_answersession in milestoneGroups
	) {
		return summary[requested_answersession];
	}

	const milestoneGroupResponse = await getMilestonegroupsForSession({
		path: {
			answersession_id: requested_answersession,
		},
	});

	if (milestoneGroupResponse.error) {
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			milestoneGroupResponse.error.detail,
			true,
			false,
		);
		return null;
	}

	milestoneGroups[requested_answersession] = {};
	for (const m of Object.values(milestoneGroupResponse.data)) {
		milestoneGroups[requested_answersession][m.id] = m;
	}

	const responseFeedback = await getSummaryFeedbackForAnswersession({
		path: {
			answersession_id: requested_answersession,
		},
	});

	if (responseFeedback.error) {
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			responseFeedback.error.detail,
			true,
			false,
		);
		return null;
	}

	return responseFeedback.data;
}

/**
 * load the detailed feedback from the database for the child, i.e., the feedback on the milestones themselves, not just the groups.
 * @param {number} requested_answersession - Answersessionkey for which we want to load the summary feedback
 * @return {Promise<Record<number, Record<number, number>> | null>} The detailed feedback for the requested answersession
 */
async function loadDetailedFeedbackFor(
	requested_answersession: number,
): Promise<Record<number, Record<number, number>> | null> {
	if (requested_answersession in detailed) {
		return detailed[requested_answersession];
	}

	const response = await getDetailedFeedbackForAnswersession({
		path: {
			answersession_id: requested_answersession,
		},
	});

	if (response.error) {
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			response.error.detail,
			true,
			false,
		);
		return null;
	}

	let res = {} as Record<number, Record<number, number>>;

	// only show milestones with negative feedback
	for (const [mid, milestones] of Object.entries(response.data)) {
		res[Number(mid)] = {} as Record<number, number>;
		for (const [ms_id, ms_score] of Object.entries(milestones)) {
			if (ms_score <= 0 && ms_score !== -2) {
				res[Number(mid)][Number(ms_id)] = Number(ms_score);
			}
		}
	}

	return res;
}

/**
 * Load the data and get everything ready to render the page
 * @return { Promise<void>} nothing
 */
async function loadData(aid: number | null): Promise<void> {
	if (aid === null) {
		return;
	}

	const summary_ = await loadSummaryFeedbackFor(aid);
	if (summary_ === null) {
		alertMessage = i18n.tr.milestone.feedbackLoadingSummaryError;
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			alertMessage,
			true,
		);
		return;
	}
	summary[aid] = summary_;

	const detailed_ = await loadDetailedFeedbackFor(aid);
	if (detailed_ === null) {
		alertMessage = i18n.tr.milestone.feedbackLoadingError;
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			alertMessage,
			true,
		);
	}
	detailed[aid] = detailed_;
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
	return aid === relevant_sessionkeys[0]
		? i18n.tr.milestone.current
		: formatDate(answerSessions[aid].created_at);
}

/**
 * Generate a printable report from the feedback by concatenating all the feedbacks into a single formatted string.
 * @return { Promise<string | null>} Report as a single string or null if error
 */
async function generateReport(): Promise<string | null> {
	// load all data again
	const responseAnswerSessions = await getCompletedMilestoneAnswerSessions({
		path: { child_id: currentChild.id as number },
	});

	if (responseAnswerSessions.error) {
		alertMessage = responseAnswerSessions.error.detail;
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			alertMessage,
			true,
		);
		return null;
	}

	const allAnswerSessions = responseAnswerSessions.data;

	// await everything being loaded, then generate the report
	const report = await Promise.all(
		Object.keys(allAnswerSessions).map((aid) => loadData(Number(aid))),
	).then(() => {
		const allSessionkeys = Object.keys(allAnswerSessions)
			.sort()
			.map((x) => Number(x))
			.reverse();

		let report = "";
		// add title
		report += `<h1>${i18n.tr.milestone.reportTitle}</h1>\n\n`;
		// add today's date
		report += `${i18n.tr.milestone.date}: ${formatDate(new Date().toLocaleDateString())} \n\n`;

		// add name and age of child in the beginning
		report += `${i18n.tr.milestone.child}: ${currentChild.name}\n`;
		report += `${i18n.tr.milestone.born}: ${currentChild.month}/${currentChild.year} \n\n`;

		// iterate over all answersessions with aid:key
		for (let aid of allSessionkeys) {
			const min = Math.min(...(Object.values(summary[aid]) as number[]));
			report += `<h2>${i18n.tr.milestone.timeperiod}: ${formatDate(answerSessions[aid].created_at)}</h2> \n`;
			report += `<strong>${i18n.tr.milestone.summaryScore}:</strong> ${min === 1 ? i18n.tr.milestone.recommendOk : min === 0 ? i18n.tr.milestone.recommendWatch : min === -1 ? i18n.tr.milestone.recommendHelp : i18n.tr.milestone.notEnoughDataYet} \n\n`;

			for (let [mid, score] of Object.entries(summary[aid])) {
				// mid : score
				report += `<h3>  ${milestoneGroups[Number(aid)][Number(mid)].text[i18n.locale].title}</h3>`;
				report += `    ${score === 1 ? i18n.tr.milestone.recommendOk : score === 0 ? i18n.tr.milestone.recommendWatch : score === -1 ? i18n.tr.milestone.recommendHelp : i18n.tr.milestone.notEnoughDataYet} \n\n`;

				for (let [ms_id, ms_score] of Object.entries(
					detailed[Number(aid)][mid],
				)) {
					// ms_id : ms_score
					report += `    <strong>${
						milestoneGroups[Number(aid)][Number(mid)]?.milestones?.find(
							(element: any) => {
								return element.id === Number(ms_id);
							},
						)?.text[i18n.locale].title
					}:</strong>`;
					report += ` ${ms_score === 1 ? i18n.tr.milestone.recommendOkShort : ms_score === 0 ? i18n.tr.milestone.recommendWatchShort : ms_score === -1 ? i18n.tr.milestone.recommendHelpShort : i18n.tr.milestone.notEnoughDataYet} \n`;
				}
			}

			report += "\n";
		}

		// delete the data again that is not necessary for displaying the page to save memory
		for (let aid of Object.keys(answerSessions)) {
			if (!(Number(aid) in relevant_sessionkeys)) {
				delete summary[Number(aid)];
				delete detailed[Number(aid)];
				delete milestoneGroups[Number(aid)];
			}
		}
		return report;
	});
	return report;
}

/**
 * Print the report generated by the generateReport function, which is called internally.
 * @return {Promise<void>} Nothing
 */
async function printReport(): Promise<void> {
	const report = await generateReport();
	if (report === null) {
		return;
	}

	const printWindow = window.open("", "", "height=600,width=800");
	if (printWindow === null) {
		return;
	}
	printWindow.document.write(`<pre>${report}</pre>`);
	printWindow.document.close();
	printWindow.print();
}
</script>

<!----------------------------------------------------------------------------->
<!--------------------- Markup section: snippets for page --------------------->
<!----------------------------------------------------------------------------->

<!--Snippet defining how to display the summary evaluation depending on the value retrieved-->
{#snippet summaryEvaluationElement(symbol: any, color: string, text: string)}
    <svelte:component this={symbol} size="xl" class={`transform scale-150 ${color}`} />
    <span class="font-bold p-2 items-center justify-center">{i18n.tr.milestone.summaryScore}</span>
    <span class="font-normal p-2 items-center justify-center">{text}</span>
{/snippet}

<!--Snippet that shows the evaluation for the whole answersession: uses the minimum of the milestonegroup currently-->
{#snippet summaryEvaluation(aid: number)}
    <!-- summary is set to the minimum reached evaluation to draw attention to them.-->
    <div class="flex flex-col md:flex-row space-y-2 space-x-2 items-center justify-center w-full text-gray-700 dark:text-gray-200 m-2 p-2 mb-4 pb-4 text-sm md:text-base">
        {#if Math.min(...(Object.values(summary[aid]) as number[])) === 1}
            {@render summaryEvaluationElement(CheckCircleSolid, "text-feedback-0", i18n.tr.milestone.recommendOk)}
        {:else if Math.min(...(Object.values(summary[aid]) as number[])) === 0}
            {@render summaryEvaluationElement(QuestionCircleSolid, "text-feedback-1", i18n.tr.milestone.recommendWatch)}
        {:else if Math.min(...(Object.values(summary[aid]) as number[])) === -1}
            {@render summaryEvaluationElement(ExclamationCircleSolid, "text-feedback-2", i18n.tr.milestone.recommendHelp)}
        {:else}
            {@render summaryEvaluationElement(CloseCircleSolid, "gray", i18n.tr.milestone.notEnoughDataYet)}
        {/if}
    </div>
    <Hr classHr="w-full my-1"/>
{/snippet}

<!--Snippet defining how to render detailed milestone feedback with help button-->
{#snippet milestoneHelpButton(milestone_or_group: MilestonePublic | undefined)}
	<span class =  "flex w-full m-2 p-2 justify-center" >
		<Button class = "btn-white btn-no-min-width" id="b1" onclick={()=>{
			showHelp= true;
		}}>{i18n.tr.milestone.help}</Button>
		<Modal class = "m-2 p-2" title={i18n.tr.milestone.help} bind:open={showHelp} dismissable={true}>
			{milestone_or_group?.text[i18n.locale].help}
		</Modal>
	</span>
{/snippet}

<!--element of the detailed evaluation which shows how the child fared in each milestonegroup-->
{#snippet evaluationElement(symbol: any, milestone_or_group: MilestonePublic | MilestoneGroupPublic | undefined, color: string, isMilestone: boolean = false)}
    <div class="flex flex-col items-center justify-center p-2 w-full">
        <div class="flex justify-center w-full mb-2">
            <svelte:component this={symbol} size="xl" class={`${color}`} />
        </div>
        {#if color !== "gray"}
			<div class = {`font-bold ${isMilestone? "text-white dark:text-white": ""}`} >
				{milestone_or_group?.text[i18n.locale].title}
			</div>
        {/if}
    </div>
{/snippet}

<!--Snippet defining how the evaluation for each milestonegroup is shown. 'grade' is the evaluation we get from the backend-->
{#snippet evaluation( milestone_or_group: MilestonePublic | MilestoneGroupPublic | undefined, grade: number, isMilestone: boolean,)}
    <div class={`rounded-lg space-x-2 space-y-2 justify-center p-2 pt-0 pb-0 m-2 flex flex-col text-sm text-white bg-milestone-600`}>
        {#if grade === 1}
            {@render evaluationElement(CheckCircleSolid, milestone_or_group, "text-feedback-0", isMilestone)}
        {:else if grade === 0}
            {@render evaluationElement(QuestionCircleSolid, milestone_or_group, "text-feedback-1", isMilestone)}
            {#if isMilestone}
                {@render milestoneHelpButton(milestone_or_group as MilestonePublic)}
            {/if}
        {:else if grade === -1}
            {@render evaluationElement(ExclamationCircleSolid, milestone_or_group, "text-feedback-2", isMilestone)}
            {#if isMilestone}
                {@render milestoneHelpButton(milestone_or_group as MilestonePublic)}
            {/if}
        {:else }
            {@render evaluationElement(CloseCircleSolid, milestone_or_group, "text-white", isMilestone)}
        {/if}
    </div>
{/snippet}

<!-- Individual element in the main tabs component of the page: Accordion display of milestone group feedback with detailed feedback for suboptimal milestones available on click -->
{#snippet milestoneGroupsEval(aid: number)}
    <Accordion class="grid grid-cols-1 sm:grid-cols-1 lg:grid-cols-2 gap-4">
        {#each Object.entries(summary[aid]) as [mid, score]}
            <div class="flex flex-col">
                <AccordionItem
                        activeClass="hover:scale-105 md:hover:scale-1 flex flex-col rounded-lg text-white dark:text-white bg-milestone-700 dark:bg-milestone-700 hover:bg-milestone-600 dark:hover:bg-milestone-600 items-center justify-between w-full font-medium text-left p-1"
                        inactiveClass="hover:scale-105 md:hover:scale-1 flex flex-col rounded-lg text-white dark:text-white bg-milestone-800 dark:bg-milestone-800 hover:bg-milestone-700 dark:hover:bg-milestone-700 items-center justify-between w-full font-medium text-left p-1"
                >
					<span slot="header" class="items-center flex justify-center py-1">
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
                        <Hr classHr="w-full my-1"/>
                    {/each}
                </AccordionItem>
            </div>
        {/each}
    </Accordion>
{/snippet}

<!-- Legend: a grid view with symbol | shorthand(bold) | explanation  on larger screens and | symbol | shorthand on smaller screens -->
{#snippet legend()}
    <div class="m-2 w-full text-gray-700 dark:text-gray-200 mb-4 pb-4">
        <p class="mb-4 pb-4 text-sm md:text-base">{i18n.tr.milestone.feedbackExplanation}</p>
        <div class ="grid grid-cols-[auto_1fr_2fr] gap-4">
            {#each milestonePresentation as milestone}
                <div class="flex justify-center">
                    <svelte:component this={milestone.icon} size="xl" class={milestone.class} />
                </div>
                <span class="font-bold text-sm md:text-base">{milestone.short}</span>
                <span class="hidden sm:block text-sm md:text-base">{milestone.text}</span>
                <div class="col-span-3">
                    <Hr classHr="w-full my-1" />
                </div>
            {/each}
        </div>
    </div>
{/snippet}

<!-- Middle part of the page with a buttton that enables the explanation modal for the feedback, and a heading that tells people what they can do next -->
{#snippet explanationModal()}
    <div class=" flex flex-col md:flex-row items-center text-gray-700 dark:text-gray-200 justify-between m-2 mb-4 pb-4 space-y-2">
        <h5 class="flex flex-auto font-bold text-md md:text-xl m-2 p-2">{i18n.tr.milestone.selectFeedback}</h5>

        <Button type="button" on:click={() => {
			showMoreInfo = true;
		}}
        >{i18n.tr.milestone.moreInfoOnEval}</Button>
    </div>

    <!-- Modal that shows the explanation of the feedback when the above button is clicked -->
    <Modal class = "m-2 p-2" classHeader="flex justify-between items-center p-4 md:p-5 rounded-t-lg text-gray-700 dark:text-gray-200" title={i18n.tr.milestone.info} bind:open={showMoreInfo} dismissable={true}>
        <p class ="text-gray-700 dark:text-gray-200 font-medium text-sm md:text-base">{i18n.tr.milestone.feedbackExplanationDetailed}</p>
        <p class ="text-gray-700 dark:text-gray-200 font-medium text-sm md:text-base">{i18n.tr.milestone.feedbackDetailsMilestone}</p>
        <p class ="text-gray-700 dark:text-gray-200 font-medium text-sm md:text-base" >{i18n.tr.milestone.feedbackDetailsEval}</p>
    </Modal>
{/snippet}


<!------------------------------------------------------------------------------------------------->
<!---------------------------------------- Markup section: actual page ---------------------------->
<!------------------------------------------------------------------------------------------------->

<!--topmost navigation element that lets us go back to children overview and child data-->
<Breadcrumbs data={breadcrumbdata} />

{#await sessionPromise}
    <!-- show a loading symbol if the data is not yet available-->
    <div class = "flex justify-center items-center space-x-2">
        <Spinner /> <p>{i18n.tr.childData.loadingMessage}</p>
    </div>
{:then}
    <Heading tag="h2" class = "text-xl md:text-4xl text-gray-700 dark:text-gray-200 items-center p-2 m-2 pb-4">{i18n.tr.milestone.feedbackTitle} </Heading>

    {@render legend()}

    {@render explanationModal()}

    <!--Main tabs component that displays the feedback for the milestones and milestonegroups -->
    <Tabs tabStyle="full" defaultClass="justify-center flex rounded-lg divide-x rtl:divide-x-reverse divide-gray-200 shadow-sm dark:divide-gray-700">
        <div class="flex flex-col md:flex-row justify-between text-sm md:text-base ">
            {#if relevant_sessionkeys.length=== 0}
                <p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-200">{i18n.tr.milestone.noFeedback}</p>
            {:else}
                {#each relevant_sessionkeys.slice(0, Math.min(numShownAnswersessions, relevant_sessionkeys.length)) as aid}
                    <TabItem defaultClass="font-bold m-1 p-0"
                             activeClasses="font-bold m-1 p-2 w-full group-first:rounded-s-lg group-last:rounded-e-lg text-white dark:text-white bg-additional-color-600 dark:bg-additional-color-600 border-1"
                             inactiveClasses="font-bold m-1 p-2 w-full group-first:rounded-s-lg group-last:rounded-e-lg text-white dark:text-white bg-additional-color-500 dark:bg-additional-color-500 hover:bg-additional-color-400 dark:hover:bg-additional-color-600 border-additional-color-600 dark:border-additional-color-600 border-1"
                             title={makeTitle(aid)}
                             open={aid === relevant_sessionkeys[0]}
                    >
                        {#await loadData(aid)}
                            <!-- show a loading symbol if the data is not yet available-->
                            <div class = "flex justify-center items-center space-x-2">
                                <Spinner /> <p>{i18n.tr.childData.loadingMessage}</p>
                            </div>
                        {:then _}
                            <!-- render feedback only once the promise has been resolved-->
                            {@render summaryEvaluation(aid)}
                            {@render milestoneGroupsEval(aid)}
                        {/await}
                    </TabItem>
                {/each}
            {/if}
        </div>
    </Tabs>

    <!--Button to print the report out into pdf or physical copy-->
    <div class="flex items-center justify-center w-full m-2 p-2 mb-4 pb-4">
        <Button class="btn-secondary" onclick={async () => {await printReport();}}>{i18n.tr.milestone.printReport}</Button>
    </div>
{:catch error}
    {alertStore.showAlert(
        i18n.tr.childData.alertMessageTitle,
        `${error.message}`,
        true,
        true
    )}
{/await}
