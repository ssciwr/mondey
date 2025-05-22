<svelte:options runes={true} />

<script lang="ts">
let { solid = false } = $props();
</script>

<div class="p-1 rounded-full border-[10px] border-solid border-white">
    <div class={`rounded-full h-12 w-12 ${solid ? "bg-white" : ""}`}>
    </div>
</div>
