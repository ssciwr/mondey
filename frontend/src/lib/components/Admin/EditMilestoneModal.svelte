<svelte:options runes={true}/>

<script lang="ts">
import { refreshMilestoneGroups } from "$lib/admin.svelte";
import {
	deleteMilestoneImage,
	updateMilestone,
	uploadMilestoneImage,
} from "$lib/client/services.gen";
import type { MilestoneAdmin } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import DeleteModal from "$lib/components/Admin/DeleteModal.svelte";
import EditImage from "$lib/components/Admin/EditImage.svelte";
import MilestoneExpectedAgeModal from "$lib/components/Admin/MilestoneExpectedAgeModal.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import {
	Button,
	ButtonGroup,
	Fileupload,
	InputAddon,
	Label,
	Modal,
	Range,
	Textarea,
} from "flowbite-svelte";
import { _, locales } from "svelte-i18n";

let {
	open = $bindable(false),
	milestone = $bindable(null),
}: { open: boolean; milestone: MilestoneAdmin | null } = $props();
let files: FileList | undefined = $state(undefined);
let images: Array<string> = $state([]);
let currentMilestoneImageId: number | null = $state(null as number | null);
let showDeleteMilestoneImageModal: boolean = $state(false);
let showMilestoneExpectedAgeModal: boolean = $state(false);

const textKeys = ["title", "desc", "obs", "help"];

function updateImagesToUpload(event: Event) {
	const target = event.target as HTMLInputElement;
	if (target.files) {
		images = Array.from(target.files).map((f) => URL.createObjectURL(f));
	} else {
		images = [];
	}
}

async function saveChanges() {
	if (!milestone) {
		return;
	}
	const { data, error } = await updateMilestone({ body: milestone });
	if (error) {
		console.log(error);
	} else {
		console.log(data);
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
	if (!currentMilestoneImageId) {
		return;
	}
	const { data, error } = await deleteMilestoneImage({
		path: { milestone_image_id: currentMilestoneImageId },
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		milestone.images = milestone.images.filter(
			(e) => e.id !== currentMilestoneImageId,
		);
		await refreshMilestoneGroups();
	}
}
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
        <div class="mb-5">
            <Label>{`${$_("admin.expected-age")}: ${milestone.expected_age_months}m`}</Label>
            <Range id="expected-age-months" min="1" max="72" bind:value={milestone.expected_age_months}/>
            <Button onclick={() => {showMilestoneExpectedAgeModal = true;}}>View data</Button>
        </div>
        <div class="mb-5">
            <Label for="img_upload" class="pb-2">{$_('admin.images')}</Label>
            <div class="flex flex-row">
                {#each milestone.images as milestoneImage (milestoneImage.id)}
                    <EditImage
                            filename={`m/${milestoneImage.id}.jpg`}
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
            <Fileupload
                    bind:files
                    on:change={updateImagesToUpload}
                    multiple
                    accept=".jpg, .jpeg"
                    id="img_upload"
                    class="mb-2 flex-grow-0"
            />
        </div>
    {/if}
    <svelte:fragment slot="footer">
        <SaveButton onclick={() => {open = false; saveChanges()}}/>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>

<DeleteModal bind:open={showDeleteMilestoneImageModal} onclick={deleteMilestoneImageAndUpdate}></DeleteModal>

{#key milestone}
    <MilestoneExpectedAgeModal bind:open={showMilestoneExpectedAgeModal}
                               milestoneId={milestone?.id}></MilestoneExpectedAgeModal>
{/key}
