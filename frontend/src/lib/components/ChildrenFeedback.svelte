<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestoneGroupPublic,
	type MilestonePublic,
	type ValidationError,
	getDetailedFeedbackForAnswersession,
	getExpiredMilestoneAnswerSessions,
	getMilestoneGroupsForAnswersession,
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
		.map((x) => Number(x));

	console.log("sessionkeys: ", sessionkeys);
}

async function loadSummaryFeedback(): Promise<void> {
	for (const aid of sessionkeys) {
		const milestoneGroupResponse = await getMilestoneGroupsForAnswersession({
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
		for (const m of milestoneGroupResponse.data) {
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

async function loadDetailedFeedback(): Promise<void> {
	for (const aid of sessionkeys) {
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

function formatDate(date: string): string {
	const dateObj = new Date(date);
	return [
		dateObj.getDate(),
		dateObj.getMonth() + 1,
		dateObj.getFullYear(),
	].join("-");
}

async function setup() {
	await loadAnswersessions();
	if (Object.keys(answerSessions).length === 0) {
		return;
	}
	await loadSummaryFeedback();
	await loadDetailedFeedback();

	console.log("answerSessions: ", answerSessions);
	console.log("milestoneGroups: ", milestoneGroups);
	console.log("summary: ", summary);
	console.log("detailed: ", detailed);
}

const promise = setup();
</script>

{#snippet evaluation( milestone_or_group: MilestonePublic | MilestoneGroupPublic, value: number, isMilestone: boolean)}
	{console.log(' milestonegroup: ', milestone_or_group.text[$locale as string].title, ', value: ', value)}
	<div class="text-gray-700 dark:text-gray-400 space-x-2 space-y-4 p-2 m-2">
		{#if value === 2}
			<div class="flex flex-cols space-x-2">
				<CheckCircleSolid color = "green" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold text-lg" >
					{milestone_or_group.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			<p >{$_("milestone.recommendOk")}</p>
		{:else if value === 1}
			<div class="flex flex-cols space-x-2">
				<EyeSolid color = "green" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold text-lg" >
					{milestone_or_group.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			<p>{$_("milestone.recommendOkWithCaveat")}</p>
		{:else if value === 0}
			<div class="flex flex-cols space-x-2">
				<BellActiveSolid color = "orange" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold text-lg" >
					{milestone_or_group.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			<p>{$_("milestone.recommendWatch")}</p>
			{#if isMilestone}
				<span class =  "ml-auto">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal title={$_("milestone.help")} bind:open={showHelp} >
						{milestone_or_group.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else if value === -1}
			<div class="flex flex-cols space-x-2">
				<ExclamationCircleSolid color = "orange" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold text-lg" >
					{milestone_or_group.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			<p>{$_("milestone.recommendWatchWithCaveat")}</p>
			{#if isMilestone}
				<span class =  "ml-auto">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal title={$_("milestone.help")} bind:open={showHelp} >
						{milestone_or_group.text[$locale as string].help}
					</Modal>
				</span>
			{/if}
		{:else}
			<div class="flex flex-cols space-x-2">
				<CloseCircleSolid color = "red" size="xl"/>
				<span class = "text-gray-700 dark:text-gray-400 font-bold text-lg" >
					{milestone_or_group.text[$locale as string].title}
				</span>
				<Hr class="mx-2"/>
			</div>
			<p>{$_("milestone.recommmendHelp")}</p>
			{#if isMilestone}
				<span class =  "ml-auto">
					<Button id="b1" onclick={()=>{
						showHelp= true;
					}}>{$_("milestone.help")}</Button>
					<Modal title={$_("milestone.help")} bind:open={showHelp} >
						{milestone_or_group.text[$locale as string].help}
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

	<p class="m-2 p-2 pb-4 text-gray-700 dark:text-gray-400">{$_("milestone.feedbackExplanation")}</p>

	<Accordion>
		<AccordionItem >
			<span slot="header" class = "text-gray-700 dark:text-gray-400 items-center flex justify-center" >
				<span class = "font-bold" >
					{$_("milestone.legend")}
				</span>
			</span>
			<div class="flex flex-col text-gray-700 dark:text-gray-400 items-start p-2 m-2 space-y-6 justify-center">
				<div class = "mx-2 px-2 w-full flex flex-row">
					<CheckCircleSolid color = "green" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendOk")}</p>
				</div>
				<Hr classHr= "mx-2 px-2 items-end w-full"/>
				<div class = "mx-2 px-2 w-full flex flex-row">
					<EyeSolid color = "green" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendOkWithCaveat")}</p>
				</div>
				<Hr classHr= "mx-2 px-2 items-end w-full"/>
				<div class = "mx-2 px-2 w-full flex flex-row">
					<BellActiveSolid color = "orange" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendWatch")}</p>
				</div>
				<Hr classHr= "mx-2 px-2 items-end w-full"/>
				<div class = "mx-2 px-2 w-full flex flex-row">
					<ExclamationCircleSolid color = "orange" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommendWatchWithCaveat")}</p>
				</div>
				<Hr classHr= "mx-2 px-2 items-end w-full"/>
				<div class = "mx-2 px-2 w-full flex flex-row">
					<CloseCircleSolid color = "red" size="xl" class="mx-2"/>
					<p>{$_("milestone.recommmendHelp")}</p>
				</div>
				<Hr classHr="mx-2 px-2 items-end w-full"/>
			</div>
		</AccordionItem>
	</Accordion>

	<Checkbox class= "pb-4 m-2 p-2 text-gray-700 dark:text-gray-400" bind:checked={showHistory}>{$_("milestone.showHistory")}</Checkbox>
	<Hr classHr= "mx-2"/>

	<div class="m-2 mx-auto w-full pb-4 p-2">
		<Timeline order="horizontal">
			{#each sessionkeys as aid}
				<!-- {#if showHistory === true || aid === sessionkeys[sessionkeys.length -1]} -->
					{console.log(" aid: ", aid, answerSessions[aid])}
					<TimelineItem classTime = "text-lg font-bold text-gray-700 dark:text-gray-400 m-2 p-2" date = {formatDate(answerSessions[aid].created_at)}>
						<svelte:fragment slot="icon">
							<div class="flex items-center">
								<div class="flex z-10 justify-center items-center w-6 h-6 bg-primary-200 rounded-full ring-0 ring-gray-200 dark:bg-primary-900 sm:ring-8 dark:ring-gray-400 shrink-0">
								<CalendarWeekSolid class="w-4 h-4 text-primary-600 dark:text-primary-400" />
								</div>
								<div class="hidden sm:flex w-full bg-gray-200 h-0.5 dark:bg-gray-700" ></div>
							</div>
						</svelte:fragment>

						<Accordion class="p-2 m-2">
							{#each Object.entries(summary[aid]) as [mid, score]}
								<AccordionItem >
									<span slot="header" class="text-gray-700 dark:text-gray-400 items-center flex justify-center space-x-2">
										{@render evaluation(milestoneGroups[aid][Number(mid)], score as number, false)}
									</span>
									<div class="flex-row justify-between">
										{console.log(" aid: ", aid, ", detailed[aid]: ", detailed[aid])}
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
							{/each}
						</Accordion>
					</TimelineItem>
				<!-- {/if} -->
			{/each}
		</Timeline>
	</div>
	{:catch error}
	<AlertMessage
		message = {`${alertMessage} ${error}`}
		title = {$_("childData.alertMessageTitle")}
	/>
	{/await}
{/if}
