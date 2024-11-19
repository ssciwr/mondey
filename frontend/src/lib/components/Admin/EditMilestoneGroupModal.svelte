<svelte:options runes={true} />

<script lang="ts">
import {
	milestoneGroupImageUrl,
	refreshMilestoneGroups,
} from "$lib/admin.svelte";
import {
	updateMilestoneGroupAdmin,
	uploadMilestoneGroupImage,
} from "$lib/client/services.gen";
import type { MilestoneGroupAdmin } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import ImageFileUpload from "$lib/components/DataInput/ImageFileUpload.svelte";
import {
	ButtonGroup,
	InputAddon,
	Label,
	Modal,
	Textarea,
} from "flowbite-svelte";
import { onMount } from "svelte";
import { _, locales } from "svelte-i18n";

let {
	open = $bindable(false),
	milestoneGroup,
}: { open: boolean; milestoneGroup: MilestoneGroupAdmin | null } = $props();
let files: FileList | undefined = $state(undefined);
let image: string = $state("");

const textKeys = ["title", "desc"];

onMount(() => {
	if (milestoneGroup) {
		image = milestoneGroupImageUrl(milestoneGroup.id);
	}
});

async function reloadImg(url: string) {
	await fetch(url, { cache: "reload", mode: "no-cors" });
	document.body.querySelectorAll(`img[src='${url}']`).forEach((img) => {
		(img as HTMLImageElement).src = url;
	});
}

export async function saveChanges() {
	if (!milestoneGroup) {
		return;
	}
	const { data, error } = await updateMilestoneGroupAdmin({
		body: milestoneGroup,
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		if (files && files.length > 0) {
			await uploadMilestoneGroupImage({
				body: { file: files[0] },
				path: { milestone_group_id: milestoneGroup.id },
			});
			await reloadImg(milestoneGroupImageUrl(milestoneGroup.id));
		}
		await refreshMilestoneGroups();
	}
}
</script>

<Modal title={$_('admin.edit')} bind:open autoclose size="xl">
	{#if milestoneGroup}
		{#each textKeys as textKey}
			{@const title = $_(`admin.${textKey}`)}
			<div class="mb-5">
				<Label class="mb-2">{title}</Label>
				{#each $locales as lang_id}
					<div class="mb-1">
						<ButtonGroup class="w-full">
							<InputAddon>{lang_id}</InputAddon>
							<Textarea bind:value={milestoneGroup.text[lang_id][textKey]} placeholder={title} />
						</ButtonGroup>
					</div>
				{/each}
			</div>
		{/each}
		<div class="mb-5">
			<Label for="img_upload" class="pb-2">{$_('admin.image')}</Label>
			<div class="flex flex-row">
				<img src={image} width="48" height="48" alt="MilestoneGroup" class="mx-2" />
				<ImageFileUpload
					bind:files
					bind:image
				/>
			</div>
		</div>
	{/if}
	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges} />
		<CancelButton />
	</svelte:fragment>
</Modal>
