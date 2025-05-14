<script>
let { solid = false } = $props();
</script>

<div
        style="border-radius:50%;min-height:3rem;min-width:3rem;"
        class={solid ? "bg-white" : ""}
></div>
