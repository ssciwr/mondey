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
// unsaved changes, keyed by user id
let edits = $state({} as Record<number, UserRead>);
let addingResearchGroup = $state({} as Record<number, boolean>);
let loading = $state(true);

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
let currentPage = $state(1);

function isTestAccount(user: UserRead): boolean {
	return user.email.endsWith("tester@testaccount.com");
}

function isImportedAccount(user: UserRead): boolean {
	return user.email.endsWith("@artificialimporteddata.csv");
}

const filteredUsers = $derived.by(() => {
	const search = searchTerm.trim().toLowerCase();
	return users.filter((user) => {
		const isTest = isTestAccount(user);
		const isImported = isImportedAccount(user);
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
const page = $derived(Math.min(currentPage, totalPages));
const pageUsers = $derived(
	filteredUsers.slice((page - 1) * usersPerPage, page * usersPerPage),
);

function resetPage() {
	currentPage = 1;
}

function edited(user: UserRead): UserRead {
	return edits[user.id] ?? user;
}

function toggle(user: UserRead, flag: UserFlag) {
	const current = edited(user);
	edits[user.id] = { ...current, [flag]: !current[flag] };
}

function replaceUser(user: UserRead) {
	users = users.map((u) => (u.id === user.id ? user : u));
}

async function refreshUsers() {
	const { data, error } = await getUsers();
	if (error || !data) {
		console.log(error);
	} else {
		edits = {};
		users = data;
	}
	loading = false;
}

async function updateUser(user: UserRead) {
	const changes = edited(user);
	const { data, error } = await usersPatchUser({
		body: {
			is_active: changes.is_active,
			is_verified: changes.is_verified,
			is_researcher: changes.is_researcher,
			is_superuser: changes.is_superuser,
			full_data_access: changes.full_data_access,
		},
		path: {
			id: `${user.id}`,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		delete edits[user.id];
		replaceUser(data);
	}
}

async function addResearchGroup(user: UserRead) {
	// disable the button until the research group is created, so that a double click doesn't create two
	addingResearchGroup[user.id] = true;
	const { data, error } = await createResearchGroup({
		path: {
			user_id: user.id,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		// the backend also makes the user a researcher when creating their research group
		replaceUser({ ...user, is_researcher: true, research_group_id: data.id });
		if (edits[user.id]) {
			edits[user.id] = {
				...edits[user.id],
				is_researcher: true,
				research_group_id: data.id,
			};
		}
	}
	addingResearchGroup[user.id] = false;
}

onMount(async () => {
	await refreshUsers();
});
</script>

{#snippet flagCheckbox(user: UserRead, flag: UserFlag)}
	<TableBodyCell>
		<Checkbox checked={edited(user)[flag]} onchange={() => toggle(user, flag)} />
	</TableBodyCell>
{/snippet}

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
	{i18n.tr.admin.users}
</h3>
<div class="mb-3 flex flex-wrap items-center gap-4">
	<Search
		bind:value={searchTerm}
		oninput={resetPage}
		class="min-w-80"
		placeholder={i18n.tr.admin.userSearchPlaceholder}
	/>
	<Checkbox bind:checked={showNormalAccounts} onchange={resetPage}>{i18n.tr.admin.userNormalAccounts}</Checkbox>
	<Checkbox bind:checked={showTestAccounts} onchange={resetPage}>{i18n.tr.admin.userTestAccounts}</Checkbox>
	<Checkbox bind:checked={showImportedAccounts} onchange={resetPage}>{i18n.tr.admin.userImportedAccounts}</Checkbox>
	<Label class="flex items-center gap-2">
		{i18n.tr.admin.userRole}
		<Select
			class="w-48"
			items={roleOptions}
			bind:value={role}
			onchange={resetPage}
			placeholder=""
			data-testid="userRoleSelect"
		/>
	</Label>
	{#if !loading}
		<span class="text-sm text-gray-700 dark:text-gray-400">
			{filteredUsers.length} / {users.length}
		</span>
	{/if}
</div>
{#if loading}
	<div class="flex justify-center items-center h-32" data-testid="usersLoading">
		<Spinner size="8" />
	</div>
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
							<Alert border={edited(user).is_researcher} color="gray">
								{user.research_group_id}
							</Alert>
								{:else if edited(user).is_researcher}
								<Button disabled={addingResearchGroup[user.id]} onclick={() => addResearchGroup(user)}>{i18n.tr.admin.addResearchCode}</Button>
							{/if}
						</TableBodyCell>
						{@render flagCheckbox(user, "is_superuser")}
						<TableBodyCell>
							<SaveButton disabled={!edits[user.id]} onclick={() => updateUser(user)} />
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
			previousLabel={i18n.tr.milestone.prev}
			nextLabel={i18n.tr.milestone.next}
		/>
	{/if}
{/if}
