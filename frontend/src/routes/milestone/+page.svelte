<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';
	import { getMilestoneGroups } from '$lib/client/services.gen';
	import type { MilestoneGroupPublic } from '$lib/client/types.gen';
	import Milestone from '$lib/components/Milestone.svelte';

	let milestoneGroup = $state(undefined as MilestoneGroupPublic | undefined);
	onMount(async () => {
		const { data, error } = await getMilestoneGroups();
		if (error || data === undefined) {
			console.log(error);
		} else {
			milestoneGroup = data[0];
		}
	});
</script>

<div class="flex items-center justify-center">
	{#key milestoneGroup}
		<Milestone {milestoneGroup} />
	{/key}
</div>
