<svelte:options runes={true}/>

<script lang="ts">
import { submitMilestoneImage } from "$lib/client/services.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import ImageFileUpload from "$lib/components/DataInput/ImageFileUpload.svelte";
import { Checkbox, Modal } from "flowbite-svelte";
import { _ } from "svelte-i18n";

let {
	open = $bindable(false),
	milestoneId,
}: { open: boolean; milestoneId: number | undefined } = $props();
let files: FileList | undefined = $state(undefined);
let image: string = $state("");
let agreeToConditions: boolean = $state(false);

export async function submitImage() {
	if (!milestoneId || !files || files.length < 1) {
		return;
	}
	const { data, error } = await submitMilestoneImage({
		body: {
			file: files[0],
		},
		path: {
			milestone_id: milestoneId,
		},
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
	}
}
</script>

<Modal title={$_('milestone.submit-image')} bind:open outsideclose size="lg">
    <div class="mb-2">
        <p>{$_('milestone.submit-image-text')}</p>
    </div>
    {#if milestoneId}
        <div class="mb-5">
            {#if image}
                <img src={image} width="128" height="128" alt="Milestone" class="m-2"/>
            {/if}
            <ImageFileUpload
                    bind:files
                    bind:image
            />
        </div>
        <Checkbox bind:checked={agreeToConditions}>{$_('milestone.submit-image-conditions')}</Checkbox>
    {/if}
    <svelte:fragment slot="footer">
        <SaveButton text={$_("milestone.submit-image")} disabled={!agreeToConditions} onclick={() => {open = false; submitImage()}}/>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>
