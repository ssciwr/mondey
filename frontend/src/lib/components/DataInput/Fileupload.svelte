<svelte:options runes={true} />
<script lang="ts">
import { Fileupload } from "flowbite-svelte";

let {
	value = $bindable(),
	accept = ".jpg, .jpeg, .png",
	innerClass = "",
}: { value: any; innerClass: string | null; accept: string } = $props();
</script>

<Fileupload
	class={innerClass}
	accept={accept}
	id="img_upload"
	on:change={(event) => {
		if (!(event.target === null)) {
			const image = event.target.files[0];
			// use https://svelte.dev/repl/b17c13d4f1bb40799ccf09e0841ddd90?version=4.2.19
			let reader = new FileReader();
			reader.readAsDataURL(image);
			reader.onload = (e) => {
				value = e.target.result;
			};
		}
	}}
/>
