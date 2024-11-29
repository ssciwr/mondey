<svelte:options runes={true} />
<script lang="ts">
import {
	type AgeInterval,
	createAgeInterval,
	deleteAgeInterval,
	getAgeIntervals,
} from "$lib/client";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import EditAgeIntervalModal from "$lib/components/Admin/EditAgeIntervalModal.svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import {
	Card,
	Hr,
	Spinner,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import { _ } from "svelte-i18n";
import DeleteModal from "./DeleteModal.svelte";
import EditButton from "./EditButton.svelte";

let alertMessage = $state($_("userData.alertMessageError"));
let showAlert = $state(false);
let openEdit = $state(false);
let openDelete = $state(false);
let ageintervals: AgeInterval[] = $state([]);
let current: number = $state(0);

async function setup(): Promise<void> {
	const ageintervalsResponse = await getAgeIntervals();

	if (ageintervalsResponse.error) {
		showAlert = true;
		alertMessage = `${$_("userData.alertMessageError")} {ageintervals.error.detail}`;
	}
	ageintervals = ageintervalsResponse.data as AgeInterval[];
}

async function addAgeInterval(): Promise<void> {
	const response = await createAgeInterval({
		query: {
			high: 0,
			low: 0,
		},
	});

	if (response.error) {
		showAlert = true;
		alertMessage = `${$_("userData.alertMessageError")} {response.error.detail}`;
		return;
	}

	ageintervals = [...ageintervals, response.data as AgeInterval];
	current = ageintervals.length - 1;
}

async function doDeleteAgeInterval(): Promise<void> {
	if (current !== null) {
		const response = await deleteAgeInterval({
			path: {
				age_interval_id: ageintervals[current].id as number,
			},
		});

		if (response.error) {
			showAlert = true;
			alertMessage = `${$_("userData.alertMessageError")} {response.error.detail}`;
			return;
		}

		ageintervals = ageintervals.filter(
			(element) => element.id !== ageintervals[current].id,
		);
		current = Math.max(current - 1, 0);
	} else {
		showAlert = true;
		alertMessage = `{$_("userData.alertMessageError")} {No interval selected}`;
		return;
	}
}

const promise = setup();
</script>

{#await promise}
	<div class="flex justify-center items-center">
	<Spinner /> <p class="text-gray-700 dark:text-gray-400">{$_("userData.loadingMessage")}</p>
	</div>
{:then}
	{#if showAlert}
		<AlertMessage
			title={$_("childData.alertMessageTitle")}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}
	<Card size="xl" class="m-5">

	<Table >
		<TableHead>
			<TableHeadCell>Id</TableHeadCell>
			<TableHeadCell>Min</TableHeadCell>
			<TableHeadCell>Max</TableHeadCell>
			<TableHeadCell>{$_('admin.actions')}</TableHeadCell>
		</TableHead>
		<TableBody>
    		{#each ageintervals as ageinterval, idx}
				<TableBodyRow>
            		<TableBodyCell>{ageinterval.id}</TableBodyCell>
            		<TableBodyCell>{ageinterval.lower_limit}</TableBodyCell>
            		<TableBodyCell>{ageinterval.upper_limit}</TableBodyCell>
					<TableBodyCell>
						<EditButton
							onclick={() => {
								current = idx;
								openEdit = true;
							}}
						/>
						<DeleteButton
							onclick={() => {
								current = idx;
								openDelete = true;
							}}
						/>

					</TableBodyCell>
				</TableBodyRow>
    		{/each}
			<TableBodyRow>
				<TableBodyCell/>
				<TableBodyCell/>
				<TableBodyCell/>
				<TableBodyCell >
					<AddButton onclick={addAgeInterval} />
				</TableBodyCell>
			</TableBodyRow>
		</TableBody>
	</Table>
    <Hr classHr="mx-2" />


	{#key openEdit}
	<EditAgeIntervalModal bind:open={openEdit} bind:interval={ageintervals[current]}/>
	{/key}
	<DeleteModal bind:open={openDelete} onclick={async ()=>{
							await doDeleteAgeInterval();
						}}/>
	</Card>
{:catch error}
	<AlertMessage
		title={"Error in server request"}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
