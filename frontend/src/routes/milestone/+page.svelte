<svelte:options runes={true} />

<script lang="ts">
import {
	getChildren,
	getCurrentMilestoneAnswerSession,
	getMilestoneGroups,
} from "$lib/client/services.gen";
import type {
	MilestoneAnswerSessionPublic,
	MilestoneGroupPublic,
} from "$lib/client/types.gen";
import Milestone from "$lib/components/Milestone.svelte";
import { onMount } from "svelte";

let milestoneGroup = $state(undefined as MilestoneGroupPublic | undefined);
let milestoneAnswerSession = $state(
	undefined as MilestoneAnswerSessionPublic | undefined,
);
let childId = $state(undefined as number | undefined);

async function updateMilestoneGroups() {
	const { data, error } = await getMilestoneGroups();
	if (error || data === undefined) {
		console.log(error);
	} else {
		milestoneGroup = data[0];
	}
}

async function updateChildId() {
	const { data, error } = await getChildren();
	if (error || data === undefined || data.length === 0) {
		console.log(error);
		childId = undefined;
	} else {
		console.log(data);
		childId = data[0].id;
	}
}

async function updateMilestoneAnswerSession() {
	await updateChildId();
	if (childId === undefined) {
		return;
	}
	const { data, error } = await getCurrentMilestoneAnswerSession({
		path: { child_id: childId },
	});
	if (error || data === undefined) {
		console.log(error);
		milestoneAnswerSession = undefined;
	} else {
		milestoneAnswerSession = data;
		console.log(data);
	}
}

onMount(async () => {
	await updateMilestoneGroups();
	await updateMilestoneAnswerSession();
});
</script>

<div class="flex items-center justify-center">
	{#key milestoneGroup}
		{#key milestoneAnswerSession}
			<Milestone {milestoneGroup} {milestoneAnswerSession} />
		{/key}
	{/key}
</div>
