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
	InfoCircleSolid,
	QuestionCircleSolid,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _, locale } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";
import Breadcrumbs from "./Navigation/Breadcrumbs.svelte";

onMount(() => {
	console.log("onmount milestonegroup: ", contentStore.milestoneGroupData);
	if (
		contentStore.milestoneGroupData &&
		contentStore.milestoneGroupData.milestones
	) {
		currentMilestone =
			contentStore.milestoneGroupData.milestones[currentMilestoneIndex];
	}
});

const imageInterval = 5000;
setInterval(() => {
	if (
		currentMilestone &&
		currentMilestone.images &&
		currentMilestone.images.length > 0
	) {
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
		currentMilestoneIndex + 1 ==
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
	const response = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});

	if (response.error) {
		console.log("Error when retrieving milestone answer session");
		showAlert = true;
		alertMessage =
			$_("milestone.alertMessageRetrieving") + " " + response.error.detail;
		milestoneAnswerSession = undefined;
	} else {
		milestoneAnswerSession = response.data;
	}
}

let milestoneAnswerSession = $state(
	null as MilestoneAnswerSessionPublic | null | undefined,
);
let currentMilestoneIndex = $state(0);
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
		label: $_("childData.overviewLabel"),
		onclick: () => {
			activeTabChildren.set("childrenGallery");
		},
	},
	{
		label: currentChild.name,
		onclick: () => {
			activeTabChildren.set("childrenRegistration");
		},
	},
	{
		label: $_("milestone.groupOverviewLabel"),
		onclick: () => {
			activeTabChildren.set("milestoneGroup");
		},
	},
	{
		label: contentStore.milestoneGroupData.text[$locale].title,
		onclick: () => {
			activeTabChildren.set("milestoneOverview");
		},
	},
	{
		label:
			String(currentMilestoneIndex + 1) +
			"/" +
			String(contentStore.milestoneGroupData.milestones.length),
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
			<div>
				{#each currentMilestone.images as image, imageIndex}
					<img
						class={`h-48 w-full object-cover transition pb-4 mb-4 duration-1000 ease-in-out md:h-96 md:w-48 md:rounded-bl-lg lg:w-72 xl:w-96 ${imageIndex === currentImageIndex ? 'opacity-100' : 'opacity-0'}`}
						src={`${import.meta.env.VITE_MONDEY_API_URL}/static/${image.filename}`}
						alt=""
					/>
				{/each}
			</div>
			<div class="m-2 md:m-4">
				<h2 class="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-400">
					{currentMilestone.text[$locale].title}
				</h2>
				<p>{currentMilestone.text[$locale].desc}</p>
				<Accordion flush>
					<AccordionItem>
						<span slot="header" class="flex gap-2 text-base">
							<InfoCircleSolid class="mt-0.5" />
							<span>{$_('milestone.observation')}</span>
						</span>
						<p>
							{currentMilestone.text[$locale].obs}
						</p>
					</AccordionItem>
					<AccordionItem>
						<span slot="header" class="flex gap-2 text-base">
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
				<div class="flex flex-row justify-center">
					<Button
						color="light"
						disabled={currentMilestoneIndex === 0}
						on:click={prevMilestone}
						class="m-1 mt-4"
					>
						<ArrowLeftOutline class="me-2 h-5 w-5" />
						{$_('milestone.prev')}
					</Button>
					<Button
						color="light"
						disabled={selectedAnswer === undefined}
						on:click={nextMilestone}
						class="m-1 mt-4"
					>
						{$_('milestone.next')}
						<ArrowRightOutline class="ms-2 h-5 w-5" />
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
