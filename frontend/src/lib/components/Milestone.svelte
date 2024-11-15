<svelte:options runes={true} />

<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
	updateMilestoneAnswer,
} from "$lib/client";
import MilestoneButton from "$lib/components/MilestoneButton.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren } from "$lib/stores/componentStore";
import { contentStore } from "$lib/stores/contentStore.svelte";
import { Accordion, AccordionItem, Button, Checkbox } from "flowbite-svelte";
import {
	ArrowLeftOutline,
	ArrowRightOutline,
	EditOutline,
	GridOutline,
	InfoCircleSolid,
	QuestionCircleSolid,
	RectangleListOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";
import Breadcrumbs from "./Navigation/Breadcrumbs.svelte";

onMount(() => {
	if (contentStore.milestoneGroupData?.milestones) {
		currentMilestone =
			contentStore.milestoneGroupData.milestones[currentMilestoneIndex];
	}
});

const imageInterval = 5000;
setInterval(() => {
	if (currentMilestone?.images && currentMilestone.images.length > 0) {
		currentImageIndex =
			(currentImageIndex + 1) % currentMilestone.images.length;
	}
}, imageInterval);

function prevMilestone() {
	if (
		!contentStore.milestoneGroupData ||
		!contentStore.milestoneGroupData.milestones ||
		currentMilestoneIndex === 0
	) {
		return;
	}
	currentMilestoneIndex -= 1;
	currentImageIndex = 0;
	currentMilestone =
		contentStore.milestoneGroupData.milestones[currentMilestoneIndex];
}

async function nextMilestone() {
	if (
		!contentStore.milestoneGroupData ||
		!contentStore.milestoneGroupData.milestones ||
		!currentMilestone ||
		selectedAnswer === undefined ||
		!milestoneAnswerSession
	) {
		return;
	}
	const { data, error } = await updateMilestoneAnswer({
		body: { milestone_id: currentMilestone.id, answer: selectedAnswer },
		path: {
			milestone_answer_session_id: milestoneAnswerSession.id,
		},
	});
	if (error) {
		console.log(error);
		return;
	}
	milestoneAnswerSession.answers[`${currentMilestone.id}`] = data;
	if (
		currentMilestoneIndex + 1 ===
		contentStore.milestoneGroupData.milestones.length
	) {
		activeTabChildren.set("milestoneOverview");
		return;
	}
	currentMilestoneIndex += 1;
	currentImageIndex = 0;
	currentMilestone =
		contentStore.milestoneGroupData.milestones[currentMilestoneIndex];
}

function selectAnswer(answer: number) {
	if (!currentMilestone) {
		console.log("selectAnswer: missing currentMilestone");
		return;
	}
	if (!milestoneAnswerSession) {
		console.log("selectAnswer: missing milestoneAnswerSession");
		return;
	}
	milestoneAnswerSession.answers[`${currentMilestone.id}`] = {
		milestone_id: currentMilestone.id,
		answer: answer,
	};
	if (selectedAnswer !== undefined && autoGoToNextMilestone) {
		nextMilestone();
	}
}

async function setup() {
	if (currentChild.id === null || currentChild.id === undefined) {
		console.log("No current child");
		return;
	}

	const response = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});

	if (response.error) {
		console.log("Error when retrieving milestone answer session");
		showAlert = true;
		alertMessage = `${$_("milestone.alertMessageRetrieving")} ${response.error.detail}`;
		milestoneAnswerSession = undefined;
	} else {
		milestoneAnswerSession = response.data;
	}
}

let milestoneAnswerSession = $state(
	null as MilestoneAnswerSessionPublic | null | undefined,
);
let currentMilestoneIndex = $state(contentStore.milestoneIndex);
let currentMilestone = $state(undefined as MilestonePublic | undefined);
let selectedAnswer = $derived(
	milestoneAnswerSession?.answers?.[`${currentMilestone?.id}`]?.answer,
);
let showAlert = $state(false);
let alertMessage = $state("");
let autoGoToNextMilestone = $state(false);
let currentImageIndex = $state(0);
const promise = setup();
const breadcrumbdata = $derived([
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: $_("milestone.groupOverviewLabel"),
		onclick: () => {
			activeTabChildren.set("milestoneGroup");
		},
		symbol: RectangleListOutline,
	},
	{
		label: contentStore.milestoneGroupData.text[$locale].title,
		onclick: () => {
			activeTabChildren.set("milestoneOverview");
		},
		symbol: GridOutline,
	},
	{
		label: `${currentMilestoneIndex + 1}/${contentStore.milestoneGroupData.milestones.length}`,
		symbol: EditOutline,
	},
]);
</script>

{#await promise}
<p>{$_("userData.loadingMessage")}</p>
{:then}
<div
	class="mx-auto flex flex-col p-4 md:rounded-t-lg"
>
	{#if $locale && contentStore.milestoneGroupData && contentStore.milestoneGroupData.text && contentStore.milestoneGroupData.milestones && currentMilestone && currentMilestone.text && currentMilestone.images}

		<Breadcrumbs data={breadcrumbdata} />

		<div class="flex w-full flex-col md:flex-row">
			<div class = "relative w-full h-48 md:h-96 md:w-48 lg:w-72 xl:w-96 overflow-hidden">
				{#each currentMilestone.images as image, imageIndex}
					<img
						class={`absolute top-0 left-0 w-full h-full object-cover transition duration-1000 ease-in-out ${imageIndex === currentImageIndex ? 'opacity-100' : 'opacity-0'}`}
						src={`${import.meta.env.VITE_MONDEY_API_URL}/static/${image.filename}`}
						alt=""
					/>
				{/each}
			</div>
			<div class="m-2 md:m-4">
				<h2 class="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-400">
					{currentMilestone.text[$locale].title}
				</h2>
				<p class="mb-2 text-base">{currentMilestone.text[$locale].desc}</p>
				<Accordion flush>
					<AccordionItem>
						<span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
							<InfoCircleSolid class="mt-0.5" />
							<span>{$_('milestone.observation')}</span>
						</span>
						<p>
							{currentMilestone.text[$locale].obs}
						</p>
					</AccordionItem>
					<AccordionItem>
						<span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
							<QuestionCircleSolid class="mt-0.5" />
							<span>{$_('milestone.help')}</span>
						</span>
						<p>
							{currentMilestone.text[$locale].help}
						</p>
					</AccordionItem>
				</Accordion>
			</div>
			<div class="m-1 flex flex-col justify-items-stretch rounded-lg">
				{#each [0, 1, 2, 3] as answerIndex}
					<MilestoneButton
						index={answerIndex}
						selected={selectedAnswer === answerIndex}
						onClick={() => {
							selectAnswer(answerIndex);
						}}
						tooltip={$_(`milestone.answer${answerIndex}-desc`)}
					>
						{$_(`milestone.answer${answerIndex}-text`)}
					</MilestoneButton>
				{/each}
				<div class="flex flex-row justify-center ">
					<Button
						color="light"
						disabled={currentMilestoneIndex === 0}
						on:click={prevMilestone}
						class="m-1 mt-4 text-gray-700 dark:text-gray-400"
					>
						<ArrowLeftOutline class="me-2 h-5 w-5 text-gray-700 dark:text-gray-400" />
						{$_('milestone.prev')}
					</Button>
					<Button
						color="light"
						disabled={selectedAnswer === undefined}
						on:click={nextMilestone}
						class="m-1 mt-4 text-gray-700 dark:text-gray-400"
					>
						{$_('milestone.next')}
						<ArrowRightOutline class="ms-2 h-5 w-5 text-gray-700 dark:text-gray-400" />
					</Button>
				</div>
				<Checkbox class="m-1 justify-center" bind:checked={autoGoToNextMilestone}>
					<p class="text-xs">{$_('milestone.autonext')}</p>
				</Checkbox>
			</div>
		</div>
	{/if}
</div>
{:catch error}
<AlertMessage message={$_("milestone.alertMessageError") + ": "+ error} />
{/await}
