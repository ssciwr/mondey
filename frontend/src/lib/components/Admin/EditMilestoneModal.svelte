<svelte:options runes={true}/>

<script lang="ts">
import { refreshMilestoneGroups } from "$lib/admin.svelte";
import {
	deleteMilestoneImage,
	updateMilestone,
	uploadMilestoneImage,
} from "$lib/client";
import type { MilestoneAdmin } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import DeleteModal from "$lib/components/Admin/DeleteModal.svelte";
import EditImage from "$lib/components/Admin/EditImage.svelte";
import MilestoneExpectedAgeModal from "$lib/components/Admin/MilestoneExpectedAgeModal.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import ImageFileUpload from "$lib/components/DataInput/ImageFileUpload.svelte";
import RangeSlider from "$lib/components/DataInput/RangeSlider.svelte";
import {
	Button,
	ButtonGroup,
	InputAddon,
	Label,
	Modal,
	Textarea,
} from "flowbite-svelte";
import { _, locales } from "svelte-i18n";

let {
	open = $bindable(false),
	milestone = $bindable(null),
}: {
	open: boolean;
	milestone: MilestoneAdmin | null;
} = $props();
let files: FileList | undefined = $state(undefined);
let images: Array<string> = $state([]);
let currentMilestoneImageId: number | null = $state(null as number | null);
let showDeleteMilestoneImageModal: boolean = $state(false);
let showMilestoneExpectedAgeModal: boolean = $state(false);

const textKeys = ["title", "desc", "obs", "help"];

async function saveChanges() {
	if (!milestone) {
		return;
	}
	const { data, error } = await updateMilestone({ body: milestone });
	if (error) {
		console.log(error);
	} else {
		if (files && files.length > 0) {
			for (const file of files) {
				await uploadMilestoneImage({
					body: { file: file },
					path: { milestone_id: milestone.id },
				});
			}
		}
		await refreshMilestoneGroups();
	}
}

async function deleteMilestoneImageAndUpdate() {
	if (!milestone || !currentMilestoneImageId) {
		return;
	}
	const { data, error } = await deleteMilestoneImage({
		path: { milestone_image_id: currentMilestoneImageId },
	});
	if (error) {
		console.log(error);
	} else {
		milestone.images = milestone.images.filter(
			(e) => e.id !== currentMilestoneImageId,
		);
		await refreshMilestoneGroups();
	}
}

let lower_age_bound = $state(0);
let upper_age_bound = $state(0);

$effect(() => {
	if (milestone !== null) {
		milestone.expected_age_months - milestone.expected_age_months_minus;
	}
});

$effect(() => {
	if (milestone !== null) {
		milestone.expected_age_months + milestone.expected_age_months_plus;
	}
});

$effect(() => {
	console.log(
		"data: ",
		milestone,
		lower_age_bound,
		upper_age_bound,
		milestone?.expected_age_months,
	);
});
</script>

<Modal title={$_('admin.edit')} bind:open size="xl" outsideclose>
    {#if milestone}
        {#each textKeys as textKey}
            {@const title = $_(`admin.${textKey}`)}
            <div class="mb-5">
                <Label class="mb-2">{title}</Label>
                {#each $locales as lang_id}
                    <div class="mb-1">
                        <ButtonGroup class="w-full">
                            <InputAddon>{lang_id}</InputAddon>
                            <Textarea bind:value={milestone.text[lang_id][textKey]} placeholder={title}/>
                        </ButtonGroup>
                    </div>
                {/each}
            </div>
        {/each}
		<div class="mb-5 space-y-2 flex flex-col">
			<Label class="pb-2">{`${$_("admin.ageIntervals")} [${lower_age_bound}m, ${upper_age_bound}m]`}</Label>
			<Label class="pb-2">{`${$_("admin.expected-age")}: ${milestone.expected_age_months}m`}</Label>
			<RangeSlider divClass="mb-2" lower={lower_age_bound} upper={upper_age_bound} central = {milestone.expected_age_months}/>
            <Button class = "mb-2 md:w-1/4 w-1/2" onclick={() => {showMilestoneExpectedAgeModal = true;}}>View data</Button>
		</div>
        <div class="mb-5">
            <Label for="img_upload" class="pb-2">{$_('admin.images')}</Label>
            <div class="flex flex-row">
                {#each milestone.images as milestoneImage (milestoneImage.id)}
                    <EditImage
                            filename={`m/${milestoneImage.id}.webp`}
                            ondelete={() => {
						currentMilestoneImageId = milestoneImage.id;
						showDeleteMilestoneImageModal = true;
				}}
                    />
                {/each}
                {#each images as image}
                    <img src={image} width="96" height="96" alt="milestone" class="w-24 h-24 m-2"/>
                {/each}
            </div>
            <ImageFileUpload bind:files bind:images multiple></ImageFileUpload>
        </div>
    {/if}
    <svelte:fragment slot="footer">
        <SaveButton onclick={() => {open = false; saveChanges()}}/>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>

<DeleteModal bind:open={showDeleteMilestoneImageModal} onclick={deleteMilestoneImageAndUpdate}></DeleteModal>

{#key milestone}
    {#if milestone}
    <MilestoneExpectedAgeModal bind:open={showMilestoneExpectedAgeModal}
                               milestoneId={milestone.id}></MilestoneExpectedAgeModal>
    {/if}
{/key}
