<svelte:options runes={true}/>

<script lang="ts">
import {
	deleteMilestoneImage,
	updateMilestone,
	uploadMilestoneImage,
} from "$lib/client/sdk.gen";
import type { MilestoneAdmin, MilestoneText } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import EditImage from "$lib/components/Admin/EditImage.svelte";
import InputAutoTranslate from "$lib/components/Admin/InputAutoTranslate.svelte";
import MilestoneExpectedAgeModal from "$lib/components/Admin/MilestoneExpectedAgeModal.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import ImageFileUpload from "$lib/components/DataInput/ImageFileUpload.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { milestoneGroups } from "$lib/stores/adminStore.svelte";
import { Button, Input, Label, Modal, Select } from "flowbite-svelte";

let {
	open = $bindable(false),
	milestone = $bindable(null),
	// called after saving when the milestone was moved to a different group, so the parent
	// can offer to recalculate statistics (this modal is torn down on save, so it cannot own
	// the recalculation modal itself)
	onGroupChanged = undefined,
}: {
	open: boolean;
	milestone: MilestoneAdmin | null;
	onGroupChanged?: () => void;
} = $props();
let files: FileList | undefined = $state(undefined);
let images: Array<string> = $state([]);
let currentMilestoneImageId: number | null = $state(null as number | null);
let showDeleteMilestoneImageModal: boolean = $state(false);
let showMilestoneExpectedAgeModal: boolean = $state(false);

// Keep the selected group local until save. `milestone` belongs to the shared store, so binding
// the select directly to it would make a canceled edit persist in frontend state.
let initialGroupId: number | null = null;
let selectedGroupId: number | null = $state(null);
let wasOpen = false;
$effect(() => {
	if (open && !wasOpen && milestone) {
		initialGroupId = milestone.group_id;
		selectedGroupId = milestone.group_id;
	}
	wasOpen = open;
});

const groupItems = $derived(
	milestoneGroups.data.map((group) => ({
		value: group.id,
		name: group.text[i18n.locale]?.title || group.text.de?.title || "",
	})),
);

const textKeys = ["title", "desc", "obs", "help", "importance"] as Array<
	keyof typeof i18n.tr.admin & keyof MilestoneText
>;

async function saveChanges(): Promise<boolean> {
	if (!milestone || selectedGroupId === null) {
		return false;
	}
	const groupChanged =
		initialGroupId !== null && selectedGroupId !== initialGroupId;
	const { error } = await updateMilestone({
		body: { ...milestone, group_id: selectedGroupId },
	});
	if (error) {
		console.log(error);
		return false;
	}

	// The milestone update is already committed. Synchronize the store and report a move before
	// attempting image uploads, whose failure must not hide the persisted group change.
	initialGroupId = selectedGroupId;
	await milestoneGroups.refresh();
	if (groupChanged) {
		onGroupChanged?.();
	}

	if (files && files.length > 0) {
		for (const file of files) {
			const { error: uploadError } = await uploadMilestoneImage({
				body: { file: file },
				path: { milestone_id: milestone.id },
			});
			if (uploadError) {
				console.log(uploadError);
				return false;
			}
		}
		await milestoneGroups.refresh();
	}
	return true;
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
		await milestoneGroups.refresh();
	}
}
</script>

<Modal title={i18n.tr.admin.edit} bind:open size="xl" outsideclose>
    {#if milestone}
        <div class="mb-5">
            <Label class="mb-2">{i18n.tr.admin.name}</Label>
            <Input bind:value={milestone.name} placeholder={i18n.tr.admin.name}/>
        </div>
        <div class="mb-5">
            <Label class="mb-2">{i18n.tr.admin.milestoneGroup}</Label>
            <Select
				data-testid="milestoneGroupSelect"
				class="mt-2"
				items={groupItems}
				bind:value={selectedGroupId}
				placeholder=""
            />
        </div>
        {#each textKeys as textKey}
            {@const title = i18n.tr.admin[textKey]}
            <div class="mb-5">
                <Label class="mb-2">{title}</Label>
                {#each i18n.locales as lang_id}
                    <div class="mb-1">
                        <InputAutoTranslate bind:value={milestone.text[lang_id][textKey]}
                                            locale={lang_id} de_text={milestone.text["de"][textKey]}
                                            placeholder={title} multiline={["obs", "help", "importance"].indexOf(textKey) !== -1} />
                    </div>
                {/each}
            </div>
        {/each}
        <div class="mb-5">
            <Label>{i18n.tr.admin.expectedAge}</Label>
            <div class="flex-row mt-2">
                {`${milestone.expected_age_months}m (${i18n.tr.admin.minRelevantAge} ${milestone.relevant_age_min}m, ${i18n.tr.admin.maxRelevantAge} ${milestone.relevant_age_max}m)`}
                <Button class="mx-4" onclick={() => {showMilestoneExpectedAgeModal = true;}}>{i18n.tr.admin.edit}</Button>
            </div>
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
		<SaveButton onclick={async () => {
			if (await saveChanges()) {
				open = false;
			}
		}}/>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>

<DeleteModal bind:open={showDeleteMilestoneImageModal} onclick={deleteMilestoneImageAndUpdate}></DeleteModal>

{#key showMilestoneExpectedAgeModal}
    {#if milestone}
        <MilestoneExpectedAgeModal bind:open={showMilestoneExpectedAgeModal} bind:milestone={milestone} />
    {/if}
{/key}
