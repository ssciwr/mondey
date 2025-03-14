<svelte:options runes={true}/>

<script lang="ts">
import { type ItemOrder } from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import { Modal } from "flowbite-svelte";
import type { DndEvent } from "svelte-dnd-action";
import { dndzone } from "svelte-dnd-action";
import { flip } from "svelte/animate";

const flipDurationMs = 100;

function handleDnd(e: CustomEvent<DndEvent>) {
	items = e.detail.items as Array<Item>;
}

type Item = { id: number; text: string };

let {
	open = $bindable(false),
	items,
	endpoint,
	callback,
}: {
	open: boolean;
	items: Array<Item>;
	endpoint: (options: any) => Promise<any>;
	callback: () => Promise<any>;
} = $props();

async function post() {
	const { data, error } = await endpoint({
		body: items.map((value, index) => {
			return { id: value.id, order: index } as ItemOrder;
		}),
	});
	if (error) {
		console.log(error);
	} else {
		await callback();
	}
}
</script>

<Modal title={i18n.tr.admin.reorder} bind:open autoclose outsideclose size="lg">
    <section use:dndzone="{{items, flipDurationMs}}" onconsider={handleDnd} onfinalize={handleDnd}>
        {#each items as item(item.id)}
            <div animate:flip="{{duration: flipDurationMs}}"
                 class="border border-1 m-2 p-2 px-4 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                {item.text}
            </div>
        {/each}
    </section>
    <svelte:fragment slot="footer">
        <SaveButton onclick={post}/>
        <CancelButton/>
    </svelte:fragment>
</Modal>
