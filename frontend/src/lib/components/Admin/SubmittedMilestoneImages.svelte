<svelte:options runes={true}/>

<script lang="ts">
import {
	approveSubmittedMilestoneImage,
	deleteSubmittedMilestoneImage,
	getSubmittedMilestoneImages,
} from "$lib/client/sdk.gen";
import type { SubmittedMilestoneImagePublic } from "$lib/client/types.gen";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { milestoneGroups } from "$lib/stores/adminStore.svelte";
import {
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import { onMount } from "svelte";

let images = $state([] as Array<SubmittedMilestoneImagePublic>);
let currentImageId = $state(0);
let showDeleteModal: boolean = $state(false);

async function refreshImages() {
	const { data, error } = await getSubmittedMilestoneImages();
	if (error || !data) {
		console.log(error);
	} else {
		images = data;
	}
}

async function deleteCurrentImage() {
	const { data, error } = await deleteSubmittedMilestoneImage({
		path: {
			submitted_milestone_image_id: currentImageId,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		await refreshImages();
	}
}

async function approveImage(image_id: number) {
	const { data, error } = await approveSubmittedMilestoneImage({
		path: {
			submitted_milestone_image_id: image_id,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		await refreshImages();
		await milestoneGroups.refresh();
	}
}

onMount(async () => {
	await refreshImages();
});
</script>

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
    {i18n.tr.admin.users}
</h3>
<Table>
    <TableHead>
        <TableHeadCell>{i18n.tr.admin.milestone}</TableHeadCell>
        <TableHeadCell>{i18n.tr.admin.image}</TableHeadCell>
        <TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
    </TableHead>
    <TableBody>
        {#each milestoneGroups.data as milestoneGroup (milestoneGroup.id)}
            {@const groupTitle = milestoneGroup.text[i18n.locale].title}
            {#each milestoneGroup.milestones as milestone (milestone.id)}
                {@const milestoneTitle = `${groupTitle} / ${milestone.text[i18n.locale].title}`}
                {#each images as image (image.id)}
                    {#if image.milestone_id === milestone.id}
                        <TableBodyRow>
                            <TableBodyCell>
                                {milestoneTitle}
                            </TableBodyCell>
                            <TableBodyCell>
                                <img src={`${import.meta.env.VITE_MONDEY_API_URL}/static/ms/${image.id}.webp`}
                                     alt={`${image.id}`}/>
                            </TableBodyCell>
                            <TableBodyCell>
                                <SaveButton text={i18n.tr.admin.approve} onclick={() => {approveImage(image.id)}}/>
                                <DeleteButton onclick={() => {
                            currentImageId = image.id;
                            showDeleteModal = true;
                        }}
                                />
                            </TableBodyCell>
                        </TableBodyRow>
                    {/if}
                {/each}
            {/each}
        {/each}
    </TableBody>
</Table>

<DeleteModal bind:open={showDeleteModal} onclick={deleteCurrentImage}></DeleteModal>
