<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';
	import {
		P,
		Breadcrumb,
		BreadcrumbItem,
		AccordionItem,
		Accordion,
		Button,
		Checkbox
	} from 'flowbite-svelte';
	import {
		QuestionCircleSolid,
		InfoCircleSolid,
		ArrowRightOutline,
		ArrowLeftOutline
	} from 'flowbite-svelte-icons';
	import type {
		MilestoneGroupPublic,
		MilestonePublic,
		MilestoneAnswerSessionPublic
	} from '$lib/client/types.gen';
	import { updateMilestoneAnswer } from '$lib/client/services.gen';
	import MilestoneButton from '$lib/components/MilestoneButton.svelte';
	import { _, locale } from 'svelte-i18n';

	let {
		milestoneGroup = undefined,
		milestoneAnswerSession = undefined
	}: {
		milestoneGroup?: MilestoneGroupPublic;
		milestoneAnswerSession?: MilestoneAnswerSessionPublic;
	} = $props();

	let currentMilestoneIndex = $state(0);
	let currentMilestone = $state(undefined as MilestonePublic | undefined);
	let selectedAnswer = $derived(
		milestoneAnswerSession?.answers?.[`${currentMilestone?.id}`]?.answer
	);
	let autoGoToNextMilestone = $state(false);
	let currentImageIndex = $state(0);

	onMount(() => {
		console.log(milestoneGroup);
		if (milestoneGroup && milestoneGroup.milestones) {
			currentMilestone = milestoneGroup.milestones[currentMilestoneIndex];
		}
	});

	const imageInterval = 5000;
	setInterval(() => {
		if (currentMilestone && currentMilestone.images && currentMilestone.images.length > 0) {
			currentImageIndex = (currentImageIndex + 1) % currentMilestone.images.length;
		}
	}, imageInterval);

	function prevMilestone() {
		if (!milestoneGroup || !milestoneGroup.milestones || currentMilestoneIndex === 0) {
			return;
		}
		currentMilestoneIndex -= 1;
		currentImageIndex = 0;
		currentMilestone = milestoneGroup.milestones[currentMilestoneIndex];
	}

	async function nextMilestone() {
		if (
			!milestoneGroup ||
			!milestoneGroup.milestones ||
			!currentMilestone ||
			selectedAnswer === undefined ||
			!milestoneAnswerSession
		) {
			return;
		}
		const { data, error } = await updateMilestoneAnswer({
			body: { milestone_id: currentMilestone.id, answer: selectedAnswer },
			path: {
				milestone_answer_session_id: milestoneAnswerSession.id
			}
		});
		if (error) {
			console.log(error);
			return;
		}
		milestoneAnswerSession.answers[`${currentMilestone.id}`] = data;
		if (currentMilestoneIndex + 1 == milestoneGroup.milestones.length) {
			console.log(`TODO: redirect to next milestone group or back to group overview`);
			// todo: redirect to bereichuebersicht? or go to next set of milestones?
			return;
		}
		currentMilestoneIndex += 1;
		currentImageIndex = 0;
		currentMilestone = milestoneGroup.milestones[currentMilestoneIndex];
	}

	function selectAnswer(answer: number | undefined) {
		if (!currentMilestone) {
			console.log('selectAnswer: missing currentMilestone');
			return;
		}
		if (!milestoneAnswerSession) {
			console.log('selectAnswer: missing milestoneAnswerSession');
			return;
		}
		milestoneAnswerSession.answers[`${currentMilestone.id}`] = {
			milestone_id: currentMilestone.id,
			answer: answer
		};
		if (selectedAnswer !== undefined && autoGoToNextMilestone) {
			nextMilestone();
		}
	}
</script>

<div
	class="border-1 flex flex-col border border-gray-200 bg-white shadow md:max-w-7xl md:rounded-lg dark:border-gray-700 dark:bg-gray-800"
>
	{#if $locale && milestoneGroup && milestoneGroup.text && milestoneGroup.milestones && currentMilestone && currentMilestone.text && currentMilestone.images}
		<div class="bg-gray-100 md:rounded-t-lg dark:bg-gray-600">
			<Breadcrumb
				olClass="inline-flex items-center space-x-1 rtl:space-x-reverse md:space-x-3 rtl:space-x-reverse flex-wrap"
				navClass="m-2"
			>
				<BreadcrumbItem href="#" home>Start</BreadcrumbItem>
				<BreadcrumbItem href="#">MEIKE</BreadcrumbItem>
				<BreadcrumbItem href="#">{$_('milestone.milestones')}</BreadcrumbItem>
				<!-- reload below is a temporary hack for demo purposes -->
				<BreadcrumbItem href="javascript:window.location.reload(true)"
					>{milestoneGroup.text[$locale].title}</BreadcrumbItem
				>
				<BreadcrumbItem
					>{currentMilestoneIndex + 1} / {milestoneGroup.milestones.length}</BreadcrumbItem
				>
			</Breadcrumb>
		</div>
		<div>
			<div class="flex w-full flex-col md:flex-row">
				<div>
					{#each currentMilestone.images as image, imageIndex}
						<img
							class={`absolute h-48 w-full object-cover transition duration-1000 ease-in-out md:h-96 md:w-48 md:rounded-bl-lg lg:w-72 xl:w-96 ${imageIndex === currentImageIndex ? 'opacity-100' : 'opacity-0'}`}
							src={`${import.meta.env.VITE_MONDEY_API_URL}/static/${image.filename}`}
							alt=""
						/>
					{/each}
					<div class="h-48 w-full md:h-96 md:w-48 md:rounded-bl-lg lg:w-72 xl:w-96"></div>
				</div>
				<div class="m-2 md:m-4">
					<h2 class="mb-2 text-2xl font-bold text-gray-700 dark:text-gray-400">
						{currentMilestone.text[$locale].title}
					</h2>
					<P>{currentMilestone.text[$locale].desc}</P>
					<Accordion flush>
						<AccordionItem>
							<span slot="header" class="flex gap-2 text-base">
								<InfoCircleSolid class="mt-0.5" />
								<span>{$_('milestone.observation')}</span>
							</span>
							<P>
								{currentMilestone.text[$locale].obs}
							</P>
						</AccordionItem>
						<AccordionItem>
							<span slot="header" class="flex gap-2 text-base">
								<QuestionCircleSolid class="mt-0.5" />
								<span>{$_('milestone.help')}</span>
							</span>
							<P>
								{currentMilestone.text[$locale].help}
							</P>
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
						<P class="text-xs">{$_('milestone.autonext')}</P>
					</Checkbox>
				</div>
			</div>
		</div>
	{/if}
</div>
