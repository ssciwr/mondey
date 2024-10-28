<script lang="ts">
	import { Fileupload } from 'flowbite-svelte';

	export let value;
</script>

<Fileupload
	class={$$props.class}
	accept={$$props.accept}
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
