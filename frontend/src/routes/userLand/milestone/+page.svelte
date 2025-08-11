<svelte:options runes={true} />

<script lang="ts">
import { goto } from "$app/navigation";
import {
	type MilestoneAnswerSessionPublic,
	type MilestonePublic,
	getCurrentMilestoneAnswerSession,
	updateMilestoneAnswer,
} from "$lib/client";
import SubmitMilestoneImageModal from "$lib/components/DataInput/SubmitMilestoneImageModal.svelte";
import MilestoneButton from "$lib/components/MilestoneButton.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { displayChildImages } from "$lib/features";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { contentStore } from "$lib/stores/contentStore.svelte";
import { Accordion, AccordionItem, Button, Modal } from "flowbite-svelte";
import {
	ArrowLeftOutline,
	ArrowRightOutline,
	EditOutline,
	ExclamationCircleSolid,
	GridOutline,
	GridPlusSolid,
	InfoCircleSolid,
	QuestionCircleSolid,
	RectangleListOutline,
	UploadOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

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
	milestoneAnswerSession.answers[`${currentMilestone.id}`] = data.answer;
	if (data.session_completed) {
		goto("/userLand/children/feedback");
		return;
	}
	if (
		currentMilestoneIndex + 1 ===
		contentStore.milestoneGroupData.milestones.length
	) {
		goto("/userLand/milestone/group");
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
		await goto("/userLand/children");
		return;
	}

	const response = await getCurrentMilestoneAnswerSession({
		path: { child_id: currentChild.id },
	});

	if (response.error) {
		console.log("Error when retrieving milestone answer session");
		alertStore.showAlert(
			i18n.tr.milestone.alertMessageError,
			`${i18n.tr.milestone.alertMessageRetrieving} ${response.error.detail}`,
			true,
			false,
		);
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
let modalImagePreviewOpen = $state(false);
let selectedAnswer = $derived(
	milestoneAnswerSession?.answers?.[`${currentMilestone?.id}`]?.answer,
);
let currentImageIndex = $state(0);
let showSubmitMilestoneImageModal = $state(false);
const promise = setup();
const breadcrumbdata = $derived([
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
		label: i18n.tr.milestone.groupOverviewLabel,
		onclick: () => {
			goto("/userLand/milestone/group");
		},
		symbol: RectangleListOutline,
	},
	{
		label: contentStore.milestoneGroupData.text[i18n.locale].title,
		onclick: () => {
			goto("/userLand/milestone/overview");
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
    <div class="mx-auto flex flex-col md:rounded-t-lg">
        {#if i18n.locale && contentStore.milestoneGroupData && contentStore.milestoneGroupData.text && contentStore.milestoneGroupData.milestones && currentMilestone && currentMilestone.text && currentMilestone.images}

            <Breadcrumbs data={breadcrumbdata} stayExpanded={true} />

            <div class="flex w-full flex-col md:flex-row pt-3">
                {#if currentMilestone.images.length > 0}
                    <div class="relative w-full h-48 md:w-1/5 md:h-48 lg:h-64 xl:h-80 2xl:h-96 overflow-hidden mt-1.5">
                        {#each currentMilestone.images as image, imageIndex}
                            <img
                                    class={` min-w-20 absolute top-0 left-0 w-full h-full object-cover transition duration-1000 ease-in-out ${imageIndex === currentImageIndex ? 'opacity-100' : 'opacity-0'}`}
                                    src={`${import.meta.env.VITE_MONDEY_API_URL}/static/m/${image.id}.webp`}
                                    alt=""
                                    on:click={() => {
                                        modalImagePreviewOpen = true;
                                    }}
                            />
                        {/each}
                        <Modal bind:open={modalImagePreviewOpen} size="xl" autoclose outsideclose>
                            <div class="p-2" on:click={()=>{modalImagePreviewOpen=false}}>
                                {#if currentMilestone?.images && currentMilestone.images.length > 0}
                                    <img
                                            class="w-full rounded-lg"
                                            src={`${import.meta.env.VITE_MONDEY_API_URL}/static/m/${currentMilestone.images[currentImageIndex].id}.webp`}
                                            alt=""
                                    />
                                {/if}
                            </div>
                        </Modal>
                    </div>
                {/if}
                <div class="m-2 md:m-4 md:w-3/5">
                    <h2 class="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-400">
                        {currentMilestone.text[i18n.locale].title}
                    </h2>
                    <p class="mb-2 text-base">{currentMilestone.text[i18n.locale].desc}</p>
                    <Accordion flush>
                        {#if currentMilestone.text[i18n.locale].obs && currentMilestone.text[i18n.locale].obs.length > 0}
                            <AccordionItem>
                            <span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
                                <InfoCircleSolid class="mt-0.5" />
                                <span>{i18n.tr.milestone.observation}</span>
                            </span>
                                <p class="whitespace-pre-line">
                                    {currentMilestone.text[i18n.locale].obs}
                                </p>
                            </AccordionItem>
                        {/if}

                        {#if currentMilestone.text[i18n.locale].help && currentMilestone.text[i18n.locale].help.length > 0}
                        <AccordionItem>
                            <span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
                                <QuestionCircleSolid class="mt-0.5" />
                                <span>{i18n.tr.milestone.help}</span>
                            </span>
                                <p class="whitespace-pre-line">
                                    {currentMilestone.text[i18n.locale].help}
                                </p>
                            </AccordionItem>
                        {/if}

                        {#if currentMilestone.text[i18n.locale].importance && currentMilestone.text[i18n.locale].importance.length > 0}
                        <AccordionItem>
                            <span slot="header" class="flex gap-2 text-base text-gray-700 dark:text-gray-400">
                                <ExclamationCircleSolid class="mt-0.5" />
                                <span>{i18n.tr.milestone.importance}</span>
                            </span>
                                <p class="whitespace-pre-line">
                                    {currentMilestone.text[i18n.locale].importance}
                                </p>
                            </AccordionItem>
                        {/if}
                        {#if displayChildImages}
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
                        {/if}
                    </Accordion>
                </div>
                <div class="md:w-1/5 m-1 mt-0 flex flex-col justify-items-stretch rounded-lg">
                    <div class="p-2 text-center md:hidden">
                        <p class="text-sm text-gray-700 dark:text-gray-400">
                            {i18n.tr.milestone.milestoneDescriptionMobileHint}
                        </p>
                    </div>
                    {#each [0, 1, 2, 3, -1] as answerIndex}
                        <MilestoneButton
                                index={answerIndex}
                                selected={selectedAnswer === answerIndex}
                                onClick={()=>{
							        selectAnswer(answerIndex);}
                                }
                                tooltip={i18n.tr.milestone[`answer${answerIndex}Desc`]}
                        >
                            {i18n.tr.milestone[`answer${answerIndex}Text`]}
                        </MilestoneButton>
                    {/each}
                    <div class="md:hidden px-2 py-1 text-sm text-left rounded-md border-gray-200 border-2 mt-4 p-2 pt-4">
                        <h4>{i18n.tr.milestone.adviceOnAnswerLevel}</h4>
                        {#each [0, 1, 2, 3, -1] as answerIndex}
                            <div class="mb-2 mt-3">
                                <div><b>
                                    <span class={`circle bg-milestone-answer-${answerIndex}`}></span>
                                    {i18n.tr.milestone[`answer${answerIndex}Text`]}:</b></div>
                                <p><small>{i18n.tr.milestone[`answer${answerIndex}Desc`]}</small></p>
                            </div>
                        {/each}
                    </div>

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
                    </div>
                </div>
            </div>
        {/if}
    </div>
{:catch error}
    {alertStore.showAlert(i18n.tr.milestone.alertMessageError, error.message, true, true, () => goto("/userLand/milestone/overview"))}
{/await}

{#key showSubmitMilestoneImageModal}
    <SubmitMilestoneImageModal bind:open={showSubmitMilestoneImageModal} milestoneId={currentMilestone?.id}/>
{/key}
