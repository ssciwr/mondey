<svelte:options runes={true} />

<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Card
	} from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';
	import ChevronUpOutline from 'flowbite-svelte-icons/ChevronUpOutline.svelte';
	import ChevronDownOutline from 'flowbite-svelte-icons/ChevronDownOutline.svelte';
	import EditMilestoneGroupModal from '$lib/components/Admin/EditMilestoneGroupModal.svelte';
	import EditMilestoneModal from '$lib/components/Admin/EditMilestoneModal.svelte';
	import DeleteModal from '$lib/components/Admin/DeleteModal.svelte';
	import AddButton from '$lib/components/Admin/AddButton.svelte';
	import EditButton from '$lib/components/Admin/EditButton.svelte';
	import DeleteButton from '$lib/components/Admin/DeleteButton.svelte';
	import { lang_id } from '$lib/stores/langStore';
	import { milestoneGroups } from '$lib/stores/adminStore';
	import { refreshMilestoneGroups, milestoneGroupImageUrl } from '$lib/admin.svelte';
	import {
		createMilestone,
		createMilestoneGroupAdmin,
		deleteMilestone,
		deleteMilestoneGroupAdmin
	} from '$lib/client/services.gen';
	import type { MilestoneAdmin, MilestoneGroupAdmin } from '$lib/client/types.gen';
	import { onMount } from 'svelte';

	let currentMilestoneGroup = $state(null as MilestoneGroupAdmin | null);
	let openMilestoneGroupIndex = $state(null as number | null);
	let showEditMilestoneGroupModal = $state(false);
	let showDeleteMilestoneGroupModal = $state(false);

	let currentMilestone = $state(null as MilestoneAdmin | null);
	let showEditMilestoneModal = $state(false);
	let showDeleteMilestoneModal = $state(false);

	function toggleOpenGroupIndex(index: number) {
		if (openMilestoneGroupIndex == index) {
			openMilestoneGroupIndex = null;
		} else {
			openMilestoneGroupIndex = index;
		}
	}

	async function addMilestoneGroup() {
		const { data, error } = await createMilestoneGroupAdmin();
		if (error || data === undefined) {
			console.log(error);
			currentMilestoneGroup = null;
			return;
		}
		console.log(data);
		currentMilestoneGroup = data;
		await refreshMilestoneGroups();
		openMilestoneGroupIndex = null;
		showEditMilestoneGroupModal = true;
	}

	async function doDeleteMilestoneGroup() {
		if (!currentMilestoneGroup) {
			console.log('No currentMilestone');
			return;
		}
		const { data, error } = await deleteMilestoneGroupAdmin({
			path: {
				milestone_group_id: currentMilestoneGroup.id
			}
		});
		if (error) {
			console.log(error);
		} else {
			console.log(data);
			await refreshMilestoneGroups();
		}
	}

	async function addMilestone(milestoneGroupId: number) {
		const { data, error } = await createMilestone({
			path: { milestone_group_id: milestoneGroupId }
		});
		if (error) {
			console.log(error);
			currentMilestone = null;
			return;
		}
		console.log(data);
		currentMilestone = data;
		showEditMilestoneModal = true;
	}

	async function doDeleteMilestone() {
		if (!currentMilestone) {
			console.log('No currentMilestone');
			return;
		}
		const { data, error } = await deleteMilestone({
			path: {
				milestone_id: currentMilestone.id
			}
		});
		if (error) {
			console.log(error);
		} else {
			console.log(data);
			await refreshMilestoneGroups();
		}
	}

	onMount(async () => {
		await refreshMilestoneGroups();
	});
</script>

<Card size="xl" class="m-5">
	{#if milestoneGroups}
		<Table>
			<TableHead>
				<TableHeadCell colSpan="4">{$_('admin.milestone-groups')}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each $milestoneGroups as milestoneGroup, groupIndex (milestoneGroup.id)}
					{@const groupTitle = milestoneGroup.text[$lang_id]?.title}
					<TableBodyRow
						on:click={() => {
							toggleOpenGroupIndex(groupIndex);
						}}
						class={`${openMilestoneGroupIndex === null || openMilestoneGroupIndex === groupIndex ? 'opacity-100' : 'opacity-25'} ${openMilestoneGroupIndex === groupIndex ? 'bg-blue-100' : ''}`}
					>
						<TableBodyCell>
							{#if openMilestoneGroupIndex === groupIndex}
								<ChevronUpOutline />
							{:else}
								<ChevronDownOutline />
							{/if}
						</TableBodyCell>
						<TableBodyCell>
							<img
								src={milestoneGroupImageUrl(milestoneGroup.id)}
								width="64"
								height="64"
								alt={groupTitle}
								class="p-2"
							/>
						</TableBodyCell>
						<TableBodyCell>
							{groupTitle}
						</TableBodyCell>
						<TableBodyCell>
							<EditButton
								onclick={(event: Event) => {
									event.stopPropagation();
									currentMilestoneGroup = milestoneGroup;
									showEditMilestoneGroupModal = true;
								}}
							/>
							<DeleteButton
								onclick={(event: Event) => {
									event.stopPropagation();
									currentMilestoneGroup = milestoneGroup;
									showDeleteMilestoneGroupModal = true;
								}}
							/>
						</TableBodyCell>
					</TableBodyRow>
					{#if openMilestoneGroupIndex === groupIndex}
						<TableBodyRow class="bg-blue-100">
							<TableBodyCell></TableBodyCell>
							<TableBodyCell colSpan="3">
								<Table>
									<TableHead>
										<TableHeadCell colspan="4">{$_('admin.milestones')}</TableHeadCell>
									</TableHead>
									<TableBody>
										{#each milestoneGroup.milestones as milestone (milestone.id)}
											{@const milestoneTitle = milestone?.text[$lang_id]?.title}
											<TableBodyRow>
												<TableBodyCell>
													{#if milestone?.images?.length}
														<img
															src={`${import.meta.env.VITE_MONDEY_API_URL}/static/${milestone.images[0].filename}`}
															width="64"
															height="64"
															alt={milestoneTitle}
															class="p-2"
														/>
													{/if}
												</TableBodyCell>
												<TableBodyCell>{milestoneTitle}</TableBodyCell>
												<TableBodyCell>
													<EditButton
														onclick={(event: Event) => {
															event.stopPropagation();
															currentMilestone = milestone;
															showEditMilestoneModal = true;
														}}
													/>
													<DeleteButton
														onclick={(event: Event) => {
															event.stopPropagation();
															currentMilestone = milestone;
															showDeleteMilestoneModal = true;
														}}
													/>
												</TableBodyCell>
											</TableBodyRow>
										{/each}
										<TableBodyRow>
											<TableBodyCell></TableBodyCell>
											<TableBodyCell></TableBodyCell>
											<TableBodyCell>
												<AddButton onclick={() => addMilestone(milestoneGroup.id)} />
											</TableBodyCell>
										</TableBodyRow>
									</TableBody>
								</Table>
							</TableBodyCell>
						</TableBodyRow>
					{/if}
				{/each}
				<TableBodyRow>
					<TableBodyCell></TableBodyCell>
					<TableBodyCell></TableBodyCell>
					<TableBodyCell></TableBodyCell>
					<TableBodyCell>
						<AddButton onclick={addMilestoneGroup} />
					</TableBodyCell>
				</TableBodyRow>
			</TableBody>
		</Table>
	{/if}
</Card>

{#key showEditMilestoneGroupModal}
	<EditMilestoneGroupModal
		bind:open={showEditMilestoneGroupModal}
		milestoneGroup={currentMilestoneGroup}
	></EditMilestoneGroupModal>
{/key}
<DeleteModal bind:open={showDeleteMilestoneGroupModal} onclick={doDeleteMilestoneGroup}
></DeleteModal>

{#key showEditMilestoneModal}
	<EditMilestoneModal bind:open={showEditMilestoneModal} milestone={currentMilestone}
	></EditMilestoneModal>
{/key}
<DeleteModal bind:open={showDeleteMilestoneModal} onclick={doDeleteMilestone}></DeleteModal>
