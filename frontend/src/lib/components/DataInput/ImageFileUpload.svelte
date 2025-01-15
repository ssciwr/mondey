<svelte:options runes={true} />

<script lang="ts">
import WarningModal from "$lib/components/WarningModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Fileupload } from "flowbite-svelte";

let {
	files = $bindable(undefined),
	images = $bindable([]),
	image = $bindable(""),
	...rest
}: {
	files: undefined | FileList;
	images?: Array<string>;
	image?: string;
} = $props();
let showWarningModal: boolean = $state(false);

function isImageFileTooLarge(file: Blob | File): boolean {
	const maxFileSizeBytes = 2 * 1024 * 1024;
	return file.size > maxFileSizeBytes;
}

function updateImagesToUpload(event: Event) {
	image = "";
	images = [];
	const target = event.target as HTMLInputElement;
	if (target.files) {
		for (const file of target.files) {
			if (isImageFileTooLarge(file)) {
				showWarningModal = true;
				files = undefined;
				return;
			}
		}
		images = Array.from(target.files).map((f) => URL.createObjectURL(f));
		image = images?.[0];
	}
}
</script>

<Fileupload
		bind:files
		on:change={updateImagesToUpload}
		accept=".jpg, .jpeg, .png"
		class="mb-2 flex-grow-0"
		{...rest}
/>
<WarningModal bind:open={showWarningModal}
			  text={`${i18n.tr.admin.maxFileSizeIs} 2 MB`}></WarningModal>
