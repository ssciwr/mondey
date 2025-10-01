<svelte:options runes={true} />

<script lang="ts">
import {
	createEvent,
	deleteEvent,
	getEvents,
	updateEvent,
} from "$lib/client/sdk.gen";
import type {
	CalendarEventCreate,
	CalendarEventRead,
	CalendarEventUpdate,
} from "$lib/client/types.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import {
	Button,
	Datepicker,
	Input,
	Label,
	Modal,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
	Textarea,
} from "flowbite-svelte";
import { DateTime } from "luxon";
import { onMount } from "svelte";

let calendarEvents = $state([] as CalendarEventRead[]);
let isLoading = $state(false);
let error = $state(null as string | null);
let successMessage = $state(null as string | null);

let showEditModal = $state(false);
let showDeleteModal = $state(false);
let currentCalendarEvent = $state(null as CalendarEventRead | null);

let editForm = $state({
	title: "",
	description: "",
	external_link: "",
	event_date: undefined as Date | undefined,
});

async function loadCalendarEvents() {
	isLoading = true;
	error = null;

	try {
		const { data, error: apiError } = await getEvents();
		if (apiError || data === undefined) {
			error = `${i18n.tr.admin.calendarEventLoadError}: ${apiError || "Unknown error"}`;
			calendarEvents = [];
		} else {
			calendarEvents = data;
		}
	} catch (e) {
		error = `${i18n.tr.admin.calendarEventLoadError}: ${e instanceof Error ? e.message : String(e)}`;
		calendarEvents = [];
	} finally {
		isLoading = false;
	}
}

function openEditModal(calendarEvent: CalendarEventRead | null = null) {
	currentCalendarEvent = calendarEvent;
	if (calendarEvent) {
		editForm.title = calendarEvent.title || "";
		editForm.description = calendarEvent.description || "";
		editForm.external_link = calendarEvent.external_link || "";
		editForm.event_date = parseISODateToDate(calendarEvent.event_date);
	} else {
		editForm.title = "";
		editForm.description = "";
		editForm.external_link = "";
		editForm.event_date = "";
	}
	showEditModal = true;
}

function openDeleteModal(calendarEvent: CalendarEventRead) {
	currentCalendarEvent = calendarEvent;
	showDeleteModal = true;
}

async function saveCalendarEvent() {
	try {
		if (currentCalendarEvent) {
			const updateData: CalendarEventUpdate = {
				title: editForm.title,
				description: editForm.description,
				external_link: editForm.external_link || "",
				event_date: editForm.event_date
					? formatDateToISOString(editForm.event_date)
					: null,
			};

			const { error: apiError } = await updateEvent({
				path: { event_id: currentCalendarEvent.id },
				body: updateData,
			});

			if (apiError) {
				alertStore.showAlert(
					`${i18n.tr.admin.calendarEventUpdateError}: ${apiError}`,
					"",
					true,
					true,
				);
				return;
			}

			successMessage = i18n.tr.admin.calendarEventUpdatedSuccess;
			setTimeout(() => {
				successMessage = null;
			}, 5000);
		} else {
			const createData: CalendarEventCreate = {
				title: editForm.title,
				description: editForm.description,
				external_link: editForm.external_link,
				event_date: editForm.event_date
					? formatDateToISOString(editForm.event_date)
					: "",
			};

			const { error: apiError } = await createEvent({
				body: createData,
			});

			if (apiError) {
				alertStore.showAlert(
					`${i18n.tr.admin.calendarEventCreateError}: ${apiError}`,
					"",
					true,
					true,
				);
				return;
			}

			successMessage = i18n.tr.admin.calendarEventCreatedSuccess;
			setTimeout(() => {
				successMessage = null;
			}, 5000);
		}

		showEditModal = false;
		await loadCalendarEvents();
	} catch (e) {
		alertStore.showAlert(
			`${i18n.tr.admin.calendarEventCreateError}: ${e instanceof Error ? e.message : String(e)}`,
			"",
			true,
			true,
		);
	}
}

async function confirmDeleteCalendarEvent() {
	if (!currentCalendarEvent) return;

	try {
		const { error: apiError } = await deleteEvent({
			path: { event_id: currentCalendarEvent.id },
		});

		if (apiError) {
			alertStore.showAlert(
				`${i18n.tr.admin.calendarEventDeleteError}: ${apiError}`,
				"",
				true,
				true,
			);
			return;
		}

		successMessage = i18n.tr.admin.calendarEventDeletedSuccess;
		setTimeout(() => {
			successMessage = null;
		}, 5000);
		showDeleteModal = false;
		await loadCalendarEvents();
	} catch (e) {
		alertStore.showAlert(
			`${i18n.tr.admin.calendarEventDeleteError}: ${e instanceof Error ? e.message : String(e)}`,
			"",
			true,
			true,
		);
	}
}

function formatDateGerman(isoDateString: string): string {
	return DateTime.fromISO(isoDateString).setLocale("de").toFormat("dd.MM.yyyy");
}

function parseISODateToDate(isoDateString: string): Date {
	return DateTime.fromISO(isoDateString).toJSDate();
}

function formatDateToISOString(date: Date): string {
	return DateTime.fromJSDate(date).toFormat("yyyy-MM-dd");
}

onMount(() => {
	loadCalendarEvents();
});
</script>

{#if isLoading}
	<div class="flex justify-center items-center py-8">
		<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
	</div>
{:else if error}
	<AlertMessage message={error} isError={true} />
{:else}
	<div class="space-y-4">
		<div class="flex justify-between items-center">
			<h3 h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{i18n.tr.admin.calendarEvents}</h3>
			<AddButton onclick={() => openEditModal()} />
		</div>

		{#if successMessage}
			<div class="px-4 py-2 bg-green-100 border border-green-400 text-green-700 rounded-lg">
				{successMessage}
			</div>
		{/if}

		<Table>
			<TableHead>
				<TableHeadCell>{i18n.tr.admin.title}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.calendarEventDate}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.desc}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.calendarEventExternalLink}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each calendarEvents as calendarEvent (calendarEvent.id)}
					<TableBodyRow>
						<TableBodyCell>{calendarEvent.title || "—"}</TableBodyCell>
						<TableBodyCell>{formatDateGerman(calendarEvent.event_date)}</TableBodyCell>
						<TableBodyCell>
							{calendarEvent.description
								? calendarEvent.description.length > 50
									? calendarEvent.description.substring(0, 50) + "..."
									: calendarEvent.description
								: "—"}
						</TableBodyCell>
						<TableBodyCell>
							{#if calendarEvent.external_link}
								<a href={calendarEvent.external_link} target="_blank" class="text-blue-600 hover:underline">
									{i18n.tr.frontpage.openLink}
								</a>
							{:else}
								—
							{/if}
						</TableBodyCell>
						<TableBodyCell>
							<div class="flex space-x-2">
								<EditButton onclick={() => openEditModal(calendarEvent)} />
								<DeleteButton onclick={() => openDeleteModal(calendarEvent)} />
							</div>
						</TableBodyCell>
					</TableBodyRow>
				{:else}
					<TableBodyRow>
						<TableBodyCell colspan="5" class="text-center text-gray-500">
							{i18n.tr.admin.calendarEventsNotFound}
						</TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
{/if}

<Modal bind:open={showEditModal} size="lg">
	<form on:submit|preventDefault={saveCalendarEvent}>
		<h3 class="text-xl font-semibold mb-4">
			{currentCalendarEvent ? i18n.tr.admin.editCalendarEvent : i18n.tr.admin.addCalendarEvent}
		</h3>

		<div class="space-y-4">
			<div>
				<Label for="title" class="mb-2">{i18n.tr.admin.title}</Label>
				<Input id="title" bind:value={editForm.title} placeholder={i18n.tr.admin.title} />
			</div>

			<div>
				<Label for="event_date" class="mb-2">{i18n.tr.admin.calendarEventDate} *</Label>
				<Datepicker
					bind:value={editForm.event_date}
					availableFrom={new Date()}
					locale="de-DE"
					translationLocale="de-DE"
					required
				/>
			</div>

			<div>
				<Label for="description" class="mb-2">{i18n.tr.admin.desc}</Label>
				<Textarea
					id="description"
					bind:value={editForm.description}
					placeholder={i18n.tr.admin.desc}
					rows="3"
				/>
			</div>

			<div>
				<Label for="external_link" class="mb-2">{i18n.tr.admin.calendarEventExternalLink}</Label>
				<Input
					id="external_link"
					type="url"
					bind:value={editForm.external_link}
					placeholder="https://example.com"
				/>
			</div>
		</div>

		<div class="flex justify-end space-x-2 mt-6">
			<Button color="alternative" on:click={() => (showEditModal = false)}>
				{i18n.tr.admin.cancel}
			</Button>
			<Button type="submit">
				{currentCalendarEvent ? i18n.tr.admin.saveChanges : i18n.tr.admin.add}
			</Button>
		</div>
	</form>
</Modal>

<DeleteModal
	bind:open={showDeleteModal}
	onclick={confirmDeleteCalendarEvent}
/>
