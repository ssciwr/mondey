<svelte:options runes={true}/>

<script lang="ts">
import { refreshMilestoneGroups } from "$lib/admin.svelte";
import {
	deleteMilestoneImage,
	updateMilestone,
	uploadMilestoneImage,
} from "$lib/client/services.gen";
import type { MilestoneAdmin, MilestoneText } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import EditImage from "$lib/components/Admin/EditImage.svelte";
import InputAutoTranslate from "$lib/components/Admin/InputAutoTranslate.svelte";
import MilestoneExpectedAgeModal from "$lib/components/Admin/MilestoneExpectedAgeModal.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import ImageFileUpload from "$lib/components/DataInput/ImageFileUpload.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import {
	Button,
	ButtonGroup,
	InputAddon,
	Label,
	Modal,
	Range,
	Textarea,
} from "flowbite-svelte";

let {
	open = $bindable(false),
	milestone = $bindable(null),
}: { open: boolean; milestone: MilestoneAdmin | null } = $props();
let files: FileList | undefined = $state(undefined);
let images: Array<string> = $state([]);
let currentMilestoneImageId: number | null = $state(null as number | null);
let showDeleteMilestoneImageModal: boolean = $state(false);
let showMilestoneExpectedAgeModal: boolean = $state(false);

const textKeys = ["title", "desc", "obs", "help"] as Array<
	keyof typeof i18n.tr.admin & keyof MilestoneText
>;

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
</script>

<Modal title={i18n.tr.admin.edit} bind:open size="xl" outsideclose>
    {#if milestone}
        {#each textKeys as textKey}
            {@const title = i18n.tr.admin[textKey]}
            <div class="mb-5">
                <Label class="mb-2">{title}</Label>
                {#each i18n.locales as lang_id}
                    <div class="mb-1">
                        <InputAutoTranslate bind:value={milestone.text[lang_id][textKey]} locale={lang_id} de_text={milestone.text["de"][textKey]} placeholder={title} />
                    </div>
                {/each}
            </div>
        {/each}
        <div class="mb-5">
            <Label>{`${i18n.tr.admin.expectedAge}: ${milestone.expected_age_months}m`}</Label>
            <Range id="expectedAge-months" min="1" max="72" bind:value={milestone.expected_age_months}/>
            <Button onclick={() => {showMilestoneExpectedAgeModal = true;}}>View data</Button>
        </div>
        <div class="mb-5">
            <Label for="img_upload" class="pb-2">{i18n.tr.admin.images}</Label>
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
