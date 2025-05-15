<svelte:options runes={true} />

<script lang="ts">
import {
	milestoneGroupImageUrl,
	refreshMilestoneGroups,
} from "$lib/admin.svelte";
import {
	createMilestone,
	createMilestoneGroupAdmin,
	deleteMilestone,
	deleteMilestoneGroupAdmin,
	orderMilestoneGroupsAdmin,
	orderMilestonesAdmin,
} from "$lib/client/sdk.gen";
import type {
	MilestoneAdmin,
	MilestoneGroupAdmin,
} from "$lib/client/types.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import EditMilestoneGroupModal from "$lib/components/Admin/EditMilestoneGroupModal.svelte";
import EditMilestoneModal from "$lib/components/Admin/EditMilestoneModal.svelte";
import OrderItemsModal from "$lib/components/Admin/OrderItemsModal.svelte";
import ReorderButton from "$lib/components/Admin/ReorderButton.svelte";
import DangerousDeleteModal from "$lib/components/DangerousDeleteModal.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
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

async function doDeleteMilestone(dry_run = true) {
	if (!currentMilestone) {
		console.log("No currentMilestone");
		return;
	}
	const { data, error } = await deleteMilestone({
		path: {
			milestone_id: currentMilestone.id,
			dry_run: dry_run,
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

{#if i18n.locale}
{#if milestoneGroups}
	<Table>
		<TableHead>
			<TableHeadCell colSpan="4">{i18n.tr.admin.milestoneGroups}</TableHeadCell>
		</TableHead>
		<TableBody>
			{#each $milestoneGroups as milestoneGroup, groupIndex (milestoneGroup.id)}
				{@const groupTitle = milestoneGroup.text[i18n.locale]?.title}
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
									<TableHeadCell colspan="4">{i18n.tr.admin.milestones}</TableHeadCell>
								</TableHead>
								<TableBody>
									{#each milestoneGroup.milestones as milestone (milestone.id)}
										{@const milestoneTitle = milestone?.text[i18n.locale]?.title}
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
											<ReorderButton
													onclick={(event: Event) => {
														event.stopPropagation();
														currentOrderEndpoint = orderMilestonesAdmin;
														currentOrderItems = milestoneGroup.milestones.map((milestone) => {return {id: milestone.id, text: milestone.text[i18n.locale]?.title};});
														showOrderItemsModal = true;
													}} />
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
					<ReorderButton
							onclick={(event: Event) => {
								event.stopPropagation();
								currentOrderEndpoint = orderMilestoneGroupsAdmin;
								currentOrderItems = $milestoneGroups.map((milestoneGroup) => {return {id: milestoneGroup.id, text: milestoneGroup.text[i18n.locale]?.title};});
								showOrderItemsModal = true;
							}} />
					<AddButton onclick={addMilestoneGroup} />
				</TableBodyCell>
			</TableBodyRow>
		</TableBody>
	</Table>
{/if}

{#key showEditMilestoneGroupModal}
	<EditMilestoneGroupModal
		bind:open={showEditMilestoneGroupModal}
		milestoneGroup={currentMilestoneGroup}
	></EditMilestoneGroupModal>
{/key}
<DangerousDeleteModal bind:open={showDeleteMilestoneGroupModal} intendedConfirmCode={i18n.tr.admin.milestones}
  deleteDryRunnableRequest={(dry_run) => deleteMilestoneGroupAdmin({
		path: {
			milestone_group_id: currentMilestoneGroup.id
		},
		query: {
			dry_run: dry_run
		}
	})} afterDelete={() => refreshMilestoneGroups()}
></DangerousDeleteModal>

{#key showEditMilestoneModal}
	<EditMilestoneModal bind:open={showEditMilestoneModal} bind:milestone={currentMilestone}
	></EditMilestoneModal>
{/key}
<DangerousDeleteModal bind:open={showDeleteMilestoneModal} intendedConfirmCode={i18n.tr.admin.milestone} deleteDryRunnableRequest={(dry_run) =>
 deleteMilestone({
		path: {
			milestone_id: currentMilestone.id,
		},
		query: {
			dry_run: dry_run
		}})} afterDelete={() => refreshMilestoneGroups()}>
</DangerousDeleteModal>

<OrderItemsModal bind:open={showOrderItemsModal} items={currentOrderItems} endpoint={currentOrderEndpoint} callback={refreshMilestoneGroups}  />
{:else}
 <AlertMessage title={i18n.tr.userData.alertMessageTitle} message={i18n.tr.userData.alertMessageError} />
{/if}
