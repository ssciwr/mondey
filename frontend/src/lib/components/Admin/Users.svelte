<svelte:options runes={true} />

<script lang="ts">
import {
	Alert,
	Button,
	Checkbox,
	Label,
	PaginationNav,
	Search,
	Select,
	type SelectOptionType,
	Spinner,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";
import SaveButton from "#lib/components/Admin/SaveButton.svelte";

import { onMount } from "svelte";
import {
	createResearchGroup,
	getUsers,
	usersPatchUser,
} from "#lib/client/sdk.gen.ts";
import type { UserRead } from "#lib/client/types.gen.ts";
import { i18n } from "#lib/i18n.svelte.ts";
import { isImportedAccountEmail, isTestAccountEmail } from "#lib/util.ts";

type UserRole = "all" | "researcher" | "admin";

type UserFlag =
	| "is_active"
	| "is_verified"
	| "is_researcher"
	| "full_data_access"
	| "is_superuser";

const usersPerPage = 50;

// saved users as returned by the backend: not deeply reactive, since there can be thousands of them
let users = $state.raw([] as Array<UserRead>);
// unsaved changes keyed by user id: only flags that differ from the saved user are stored
let edits = $state({} as Record<number, Partial<Record<UserFlag, boolean>>>);
let pendingUserActions = $state({} as Record<number, boolean>);
let loading = $state(true);
let loadError = $state(false);

let searchTerm = $state("");
// show users with any of the checked account types
let showNormalAccounts = $state(true);
let showTestAccounts = $state(false);
let showImportedAccounts = $state(false);
let role = $state("all" as UserRole);
const roleOptions: Array<SelectOptionType<UserRole>> = $derived([
	{ value: "all", name: i18n.tr.admin.userRoleAll },
	{ value: "researcher", name: i18n.tr.admin.userResearcher },
	{ value: "admin", name: i18n.tr.admin.userAdmin },
]);

const filteredUsers = $derived.by(() => {
	const search = searchTerm.trim().toLowerCase();
	return users.filter((user) => {
		const isTest = isTestAccountEmail(user.email);
		const isImported = isImportedAccountEmail(user.email);
		return (
			(!search || user.email.toLowerCase().includes(search)) &&
			((showNormalAccounts && !isTest && !isImported) ||
				(showTestAccounts && isTest) ||
				(showImportedAccounts && isImported)) &&
			(role === "all" ||
				(role === "researcher" && user.is_researcher) ||
				(role === "admin" && user.is_superuser))
		);
	});
});
const totalPages = $derived(
	Math.max(1, Math.ceil(filteredUsers.length / usersPerPage)),
);
// go back to the first page whenever a filter changes
let currentPage = $derived.by(() => {
	void [
		searchTerm,
		showNormalAccounts,
		showTestAccounts,
		showImportedAccounts,
		role,
	];
	return 1;
});
const page = $derived(Math.min(currentPage, totalPages));
const pageUsers = $derived(
	filteredUsers.slice((page - 1) * usersPerPage, page * usersPerPage),
);

function flag(user: UserRead, key: UserFlag): boolean {
	return edits[user.id]?.[key] ?? user[key] ?? false;
}

// drop any unsaved changes for this user that now match the saved user
function pruneEdits(user: UserRead) {
	const userEdits = edits[user.id];
	if (!userEdits) return;
	for (const [key, value] of Object.entries(userEdits)) {
		if (user[key as UserFlag] === value) {
			delete userEdits[key as UserFlag];
		}
	}
	if (Object.keys(userEdits).length === 0) {
		delete edits[user.id];
	}
}

function toggle(user: UserRead, key: UserFlag) {
	edits[user.id] = { ...edits[user.id], [key]: !flag(user, key) };
	pruneEdits(user);
}

function updateSavedUser(id: number, changes: Partial<UserRead>) {
	users = users.map((u) => {
		if (u.id !== id) return u;
		const updated = { ...u, ...changes };
		pruneEdits(updated);
		return updated;
	});
}

async function runUserAction(user: UserRead, action: () => Promise<void>) {
	if (pendingUserActions[user.id]) return;
	pendingUserActions[user.id] = true;
	try {
		await action();
	} finally {
		delete pendingUserActions[user.id];
	}
}

async function refreshUsers() {
	loading = true;
	loadError = false;
	const { data, error } = await getUsers();
	if (error || !data) {
		console.log(error);
		loadError = true;
	} else {
		edits = {};
		users = data;
	}
	loading = false;
}

async function updateUser(user: UserRead) {
	const { data, error } = await usersPatchUser({
		body: {
			is_active: flag(user, "is_active"),
			is_verified: flag(user, "is_verified"),
			is_researcher: flag(user, "is_researcher"),
			is_superuser: flag(user, "is_superuser"),
			full_data_access: flag(user, "full_data_access"),
		},
		path: {
			id: `${user.id}`,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		// any changes made while the request was in flight are kept as unsaved edits
		updateSavedUser(user.id, data);
	}
}

async function addResearchGroup(user: UserRead) {
	const { data, error } = await createResearchGroup({
		path: {
			user_id: user.id,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		// the backend also makes the user a researcher in the new research group
		updateSavedUser(user.id, {
			is_researcher: true,
			research_group_id: data.id,
		});
	}
}

onMount(async () => {
	await refreshUsers();
});
</script>

{#snippet flagCheckbox(user: UserRead, key: UserFlag)}
	<TableBodyCell>
		<Checkbox checked={flag(user, key)} onchange={() => toggle(user, key)} />
	</TableBodyCell>
{/snippet}

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
	{i18n.tr.admin.users}
</h3>
<div class="mb-3 flex flex-wrap items-center gap-4">
	<Search
		bind:value={searchTerm}
		class="min-w-80"
		placeholder={i18n.tr.admin.userSearchPlaceholder}
	/>
	<Checkbox bind:checked={showNormalAccounts}>{i18n.tr.admin.userNormalAccounts}</Checkbox>
	<Checkbox bind:checked={showTestAccounts}>{i18n.tr.admin.userTestAccounts}</Checkbox>
	<Checkbox bind:checked={showImportedAccounts}>{i18n.tr.admin.userImportedAccounts}</Checkbox>
	<Label class="flex items-center gap-2">
		{i18n.tr.admin.userRole}
		<Select
			class="w-48"
			items={roleOptions}
			bind:value={role}
			placeholder=""
			data-testid="userRoleSelect"
		/>
	</Label>
	{#if !loading && !loadError}
		<span class="text-sm text-gray-700 dark:text-gray-400">
			{filteredUsers.length} / {users.length}
		</span>
	{/if}
</div>
{#if loading}
	<div class="flex justify-center items-center h-32" data-testid="usersLoading">
		<Spinner size="8" />
	</div>
{:else if loadError}
	<Alert color="red" class="flex items-center gap-4" data-testid="usersLoadError">
		{i18n.tr.admin.userLoadError}
		<Button size="xs" onclick={refreshUsers}>{i18n.tr.admin.userRetry}</Button>
	</Alert>
{:else}
	<div class="overflow-x-scroll overflow-y-scroll">
		<Table class="w-max max-h-[600px]">
			<TableHead>
				<TableHeadCell>{i18n.tr.admin.userEmail}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userActive}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userVerified}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userResearcher}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userFullDataAccess}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userResearchCode}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.userAdmin}</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each pageUsers as user (user.id)}
					<TableBodyRow>
						<TableBodyCell>
							{user.email}
						</TableBodyCell>
						{@render flagCheckbox(user, "is_active")}
						{@render flagCheckbox(user, "is_verified")}
						{@render flagCheckbox(user, "is_researcher")}
						{@render flagCheckbox(user, "full_data_access")}
						<TableBodyCell>
							{#if user.research_group_id > 0}
							<Alert border={flag(user, "is_researcher")} color="gray">
								{user.research_group_id}
							</Alert>
								{:else if flag(user, "is_researcher")}
								<Button
									disabled={pendingUserActions[user.id]}
									onclick={() => runUserAction(user, () => addResearchGroup(user))}
								>{i18n.tr.admin.addResearchCode}</Button>
							{/if}
						</TableBodyCell>
						{@render flagCheckbox(user, "is_superuser")}
						<TableBodyCell>
							<SaveButton
								disabled={!edits[user.id] || pendingUserActions[user.id]}
								onclick={() => runUserAction(user, () => updateUser(user))}
							/>
						</TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
	{#if totalPages > 1}
		<PaginationNav
			class="mt-3"
			currentPage={page}
			{totalPages}
			onPageChange={(newPage) => (currentPage = newPage)}
			previousLabel={i18n.tr.admin.previousPage}
			nextLabel={i18n.tr.admin.nextPage}
		/>
	{/if}
{/if}
