<svelte:options runes={true} />
<script lang="ts">
import { Fileupload } from "flowbite-svelte";

let {
	value = $bindable(null),
	accept = ".jpg, .jpeg, .png",
	innerClass = "mb-2 flex-grow-0",
	required = false,
	disabled = false,
	clearable = false,
}: {
	value: File | string | null;
	accept?: string;
	innerClass?: string | null;
	required?: boolean;
	disabled?: boolean;
	clearable?: boolean;
} = $props();

let files: FileList | undefined = $state(undefined);

function updateImagesToUpload(event: Event) {
	const target = event.target as HTMLInputElement;
	console.log("target.files: ", target.files);
	if (target.files) {
		value = target.files[0];
	} else {
		value = null;
	}
}
</script>


<Fileupload
	class = {innerClass}
	bind:files
	on:change={updateImagesToUpload}
	accept={accept}
	id="img_upload"
	required={required}
	disabled={disabled}
	clearable = {clearable}
/>
