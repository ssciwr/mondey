<svelte:options runes={true} />

<script lang="ts">
import {
	milestoneGroupImageUrl,
	refreshMilestoneGroups,
} from "$lib/admin.svelte";
import {
	type AgeInterval,
	createMilestone,
	createMilestoneGroupAdmin,
	deleteMilestone,
	deleteMilestoneGroupAdmin,
	getAgeIntervals,
	orderMilestoneGroupsAdmin,
	orderMilestonesAdmin,
} from "$lib/client";
import type {
	MilestoneAdmin,
	MilestoneGroupAdmin,
} from "$lib/client/types.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import DeleteModal from "$lib/components/Admin/DeleteModal.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import EditMilestoneGroupModal from "$lib/components/Admin/EditMilestoneGroupModal.svelte";
import EditMilestoneModal from "$lib/components/Admin/EditMilestoneModal.svelte";
import OrderItemsModal from "$lib/components/Admin/OrderItemsModal.svelte";
import ReorderButton from "$lib/components/Admin/ReorderButton.svelte";
import { milestoneGroups } from "$lib/stores/adminStore";
import {
	Card,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import ChevronDownOutline from "flowbite-svelte-icons/ChevronDownOutline.svelte";
import ChevronUpOutline from "flowbite-svelte-icons/ChevronUpOutline.svelte";
import { onMount } from "svelte";
import { _, locale } from "svelte-i18n";
import AlertMessage from "../AlertMessage.svelte";

let currentMilestoneGroup = $state(null as MilestoneGroupAdmin | null);
let openMilestoneGroupIndex = $state(null as number | null);
let showEditMilestoneGroupModal = $state(false);
let showDeleteMilestoneGroupModal = $state(false);

let currentMilestone = $state(null as MilestoneAdmin | null);
let showEditMilestoneModal = $state(false);
let showDeleteMilestoneModal = $state(false);

let currentOrderEndpoint = $state(orderMilestonesAdmin);
let currentOrderItems = $state([] as Array<{ id: number; text: string }>);
let showOrderItemsModal = $state(false);
let ageIntervals = $state([] as AgeInterval[]);

async function doGetAgeIntervals(): Promise<void> {
	const response = await getAgeIntervals();

	if (response.error) {
		console.log(response.error);
		return;
	}
	ageIntervals = response.data as AgeInterval[];
}

onMount(async () => {
	await doGetAgeIntervals();
});

function toggleOpenGroupIndex(index: number) {
	if (openMilestoneGroupIndex === index) {
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
		console.log("No currentMilestone");
		return;
	}
	const { data, error } = await deleteMilestoneGroupAdmin({
		path: {
			milestone_group_id: currentMilestoneGroup.id,
		},
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
		path: { milestone_group_id: milestoneGroupId },
		query: {
			age_interval: 0,
		},
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
		console.log("No currentMilestone");
		return;
	}
	const { data, error } = await deleteMilestone({
		path: {
			milestone_id: currentMilestone.id,
		},
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await refreshMilestoneGroups();
	}
}
</script>

{#if $locale}
<Card size="xl" class="m-5">
	{#if milestoneGroups}
		<Table>
			<TableHead>
				<TableHeadCell colSpan="4">{$_('admin.milestone-groups')}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each $milestoneGroups as milestoneGroup, groupIndex (milestoneGroup.id)}
					{@const groupTitle = milestoneGroup.text[$locale]?.title}
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
											{@const milestoneTitle = milestone?.text[$locale]?.title}
											<TableBodyRow>
												<TableBodyCell>
													{#if milestone?.images?.length}
														<img
															src={`${import.meta.env.VITE_MONDEY_API_URL}/static/m/${milestone.images[0].id}.webp`}
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
												<ReorderButton
														onclick={(event: Event) => {
															event.stopPropagation();
															currentOrderEndpoint = orderMilestonesAdmin;
															currentOrderItems = milestoneGroup.milestones.map((milestone) => {return {id: milestone.id, text: milestone.text[$locale]?.title};});
															showOrderItemsModal = true;
														}} />
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
						<ReorderButton
								onclick={(event: Event) => {
									event.stopPropagation();
									currentOrderEndpoint = orderMilestoneGroupsAdmin;
									currentOrderItems = $milestoneGroups.map((milestoneGroup) => {return {id: milestoneGroup.id, text: milestoneGroup.text[$locale]?.title};});
									showOrderItemsModal = true;
								}} />
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
	<EditMilestoneModal bind:open={showEditMilestoneModal} bind:milestone={currentMilestone} bind:ageintervals= {ageIntervals}
	></EditMilestoneModal>

{/key}
<DeleteModal bind:open={showDeleteMilestoneModal} onclick={doDeleteMilestone}></DeleteModal>

<OrderItemsModal bind:open={showOrderItemsModal} items={currentOrderItems} endpoint={currentOrderEndpoint} callback={refreshMilestoneGroups}  />
{:else}
 <AlertMessage title={$_("userData.alertMessageTitle")} message={$_("userData.alertMessageError")} />
{/if}
