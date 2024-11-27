<svelte:options runes={true} />
<script lang="ts">
import { Modal } from "flowbite-svelte";

let { show = $bindable(false) }: { show: boolean } = $props();
let lowerBound: number | null = null;
let upperBound: number | null = null;
</script>

<Modal bind:open={show} title="Create Age Interval">
    <p>TODO</p>
</Modal>
