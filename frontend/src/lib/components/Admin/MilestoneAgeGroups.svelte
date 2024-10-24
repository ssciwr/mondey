<svelte:options runes={true} />

<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Card,
		NumberInput
	} from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';
	import DeleteModal from '$lib/components/Admin/DeleteModal.svelte';
	import AddButton from '$lib/components/Admin/AddButton.svelte';
	import SaveButton from '$lib/components/Admin/SaveButton.svelte';
	import DeleteButton from '$lib/components/Admin/DeleteButton.svelte';
	import { milestoneAgeGroups } from '$lib/admin.svelte';
	import type { MilestoneAgeGroupCreate } from '$lib/client/types.gen';
	import { onMount } from 'svelte';

	let currentMilestoneAgeGroupId = $state(null as number | null);
	let showDeleteModal = $state(false);
	let newMilestoneAgeGroup = $state({ months_min: 0, months_max: 0 } as MilestoneAgeGroupCreate);

	onMount(async () => {
		await milestoneAgeGroups.refresh();
	});
</script>

<Card size="xl" class="m-5">
	{#if milestoneAgeGroups.value}
		<Table>
			<TableHead>
				<TableHeadCell>ID</TableHeadCell>
				<TableHeadCell>{$_('admin.min-age-months')}</TableHeadCell>
				<TableHeadCell>{$_('admin.max-age-months')}</TableHeadCell>
				<TableHeadCell>{$_('admin.actions')}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each milestoneAgeGroups.value as milestoneAgeGroup (milestoneAgeGroup.id)}
					<TableBodyRow>
						<TableBodyCell>
							{milestoneAgeGroup.id}
						</TableBodyCell>
						<TableBodyCell>
							<NumberInput bind:value={milestoneAgeGroup.months_min} />
						</TableBodyCell>
						<TableBodyCell>
							<NumberInput bind:value={milestoneAgeGroup.months_max} />
						</TableBodyCell>
						<TableBodyCell>
							<SaveButton
								onclick={() => {
									milestoneAgeGroups.save(milestoneAgeGroup);
								}}
							/>
							<DeleteButton
								onclick={() => {
									currentMilestoneAgeGroupId = milestoneAgeGroup.id;
									showDeleteModal = true;
								}}
							/>
						</TableBodyCell>
					</TableBodyRow>
				{/each}
				<TableBodyRow>
					<TableBodyCell></TableBodyCell>
					<TableBodyCell>
						<NumberInput bind:value={newMilestoneAgeGroup.months_min} />
					</TableBodyCell>
					<TableBodyCell>
						<NumberInput bind:value={newMilestoneAgeGroup.months_max} />
					</TableBodyCell>
					<TableBodyCell>
						<AddButton
							onclick={() => {
								milestoneAgeGroups.create(newMilestoneAgeGroup);
							}}
						/>
					</TableBodyCell>
				</TableBodyRow>
			</TableBody>
		</Table>
	{/if}
</Card>

<DeleteModal
	bind:open={showDeleteModal}
	onclick={() => {
		if (currentMilestoneAgeGroupId) {
			milestoneAgeGroups.delete(currentMilestoneAgeGroupId);
		}
	}}
></DeleteModal>
