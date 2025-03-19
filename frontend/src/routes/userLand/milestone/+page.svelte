<svelte:options runes={true} />

<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
	updateMilestoneAnswer,
} from "$lib/client";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import SubmitMilestoneImageModal from "$lib/components/DataInput/SubmitMilestoneImageModal.svelte";
import MilestoneButton from "$lib/components/MilestoneButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage } from "$lib/stores/componentStore";
import { contentStore } from "$lib/stores/contentStore.svelte";
import { Accordion, AccordionItem, Button } from "flowbite-svelte";
import {
	ArrowLeftOutline,
	ArrowRightOutline,
	EditOutline,
	GridOutline,
	GridPlusSolid,
	InfoCircleSolid,
	QuestionCircleSolid,
	RectangleListOutline,
	UploadOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
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
		activePage.set("milestoneOverview");
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
	if (selectedAnswer !== undefined) {
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
		alertMessage = `${i18n.tr.milestone.alertMessageRetrieving} ${response.error.detail}`;
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
let currentImageIndex = $state(0);
let showSubmitMilestoneImageModal = $state(false);
const promise = setup();
const breadcrumbdata = $derived([
	{
		label: i18n.tr.childData.overviewLabel,
		onclick: () => {
			activePage.set("childrenGallery");
		},
		symbol: GridPlusSolid,
	},
	{
		label: currentChild.name,
		onclick: () => {
			activePage.set("childrenRegistration");
		},
		symbol: UserSettingsOutline,
	},
	{
		label: i18n.tr.milestone.groupOverviewLabel,
		onclick: () => {
			activePage.set("milestoneGroup");
		},
		symbol: RectangleListOutline,
	},
	{
		label: contentStore.milestoneGroupData.text[i18n.locale].title,
		onclick: () => {
			activePage.set("milestoneOverview");
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
    <p>{i18n.tr.userData.loadingMessage}</p>
{:then}
    <div
            class="mx-auto flex flex-col p-4 md:rounded-t-lg"
    >
        {#if i18n.locale && contentStore.milestoneGroupData && contentStore.milestoneGroupData.text && contentStore.milestoneGroupData.milestones && currentMilestone && currentMilestone.text && currentMilestone.images}

            <Breadcrumbs data={breadcrumbdata} />

            <div class="flex w-full flex-col md:flex-row pt-3">
                <div class="relative w-full h-48 md:h-96 md:w-24 lg:w-60 xl:w-72 overflow-hidden mt-1.5">
                    {#each currentMilestone.images as image, imageIndex}
                        <img
                                class={` min-w-20 absolute top-0 left-0 w-full h-full object-cover transition duration-1000 ease-in-out ${imageIndex === currentImageIndex ? 'opacity-100' : 'opacity-0'}`}
                                src={`${import.meta.env.VITE_MONDEY_API_URL}/static/m/${image.id}.webp`}
                                alt=""
                        />
                    {/each}
                </div>
                <div class="m-2 md:m-4 grow">
                    <h2 class="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-400">
                        {currentMilestone.text[i18n.locale].title}
                    </h2>
                    <p class="mb-2 text-base">{currentMilestone.text[i18n.locale].desc}</p>
                    <Accordion flush>
                        <AccordionItem>
						<span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
							<InfoCircleSolid class="mt-0.5" />
							<span>{i18n.tr.milestone.observation}</span>
						</span>
                            <p>
                                {currentMilestone.text[i18n.locale].obs}
                            </p>
                        </AccordionItem>
                        <AccordionItem>
						<span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
							<QuestionCircleSolid class="mt-0.5" />
							<span>{i18n.tr.milestone.help}</span>
						</span>
                            <p>
                                {currentMilestone.text[i18n.locale].help}
                            </p>
                        </AccordionItem>
                        <AccordionItem>
						<span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
							<UploadOutline class="mt-0.5"/>
							<span>{i18n.tr.milestone.submitImage}</span>
						</span>
                            <p>
                                {i18n.tr.milestone.submitImageText}
                            </p>
                            <Button class="m-2"
                                    onclick={()=>{showSubmitMilestoneImageModal=true;}}>{i18n.tr.milestone.submitImage}</Button>
                        </AccordionItem>
                    </Accordion>
                </div>
                <div class="m-1 mt-0 flex flex-col justify-items-stretch rounded-lg">
                    {#each [0, 1, 2, 3] as answerIndex}
                        <MilestoneButton
                                index={answerIndex}
                                selected={selectedAnswer === answerIndex}
                                onClick={() => {
							selectAnswer(answerIndex);
						}}
                                tooltip={i18n.tr.milestone[`answer${answerIndex}Desc`]}
                        >
                            {i18n.tr.milestone[`answer${answerIndex}Text`]}
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
                            {i18n.tr.milestone.prev}
                        </Button>
                        <Button
                                color="light"
                                disabled={selectedAnswer === null || selectedAnswer === undefined || selectedAnswer < 0}
                                on:click={nextMilestone}
                                class="m-1 mt-4 text-gray-700 dark:text-gray-400"
                        >
                            {i18n.tr.milestone.next}
                            <ArrowRightOutline class="ms-2 h-5 w-5 text-gray-700 dark:text-gray-400" />
                        </Button>
                    </div>
                </div>
            </div>
        {/if}
    </div>
{:catch error}
    <AlertMessage message={i18n.tr.milestone.alertMessageError + ": "+ error} />
{/await}

{#key showSubmitMilestoneImageModal}
    <SubmitMilestoneImageModal bind:open={showSubmitMilestoneImageModal} milestoneId={currentMilestone?.id}/>
{/key}
