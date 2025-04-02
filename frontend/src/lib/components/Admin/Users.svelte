<svelte:options runes={true} />

<script lang="ts">
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import {
	Alert,
	Button,
	Card,
	Checkbox,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";

import {
	createResearchGroup,
	getUsers,
	usersPatchUser,
} from "$lib/client/services.gen";
import type { UserRead } from "$lib/client/types.gen";
import { i18n } from "$lib/i18n.svelte";
import { onMount } from "svelte";

let users = $state([] as Array<UserRead>);
let saveDisabled = $state({} as Record<string, boolean>);

async function refreshUsers() {
	const { data, error } = await getUsers();
	if (error || !data) {
		console.log(error);
	} else {
		saveDisabled = {};
		users = data;
		for (const user of users) {
			saveDisabled[user.id] = true;
		}
	}
}

async function updateUser(user: UserRead) {
	const { data, error } = await usersPatchUser({
		body: {
			is_active: user.is_active,
			is_verified: user.is_verified,
			is_researcher: user.is_researcher,
			is_superuser: user.is_superuser,
			full_data_access: user.full_data_access,
		},
		path: {
			id: `${user.id}`,
		},
	});
	if (error || !data) {
		console.log(error);
	} else {
		await refreshUsers();
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
		await refreshUsers();
	}
}

onMount(async () => {
	await refreshUsers();
});
</script>

<Card size="xl" class="m-5 w-full">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
		{i18n.tr.admin.users}
	</h3>
	<div class="overflow-x-scroll overflow-y-scroll">
		<Table class="w-max max-h-[600px]">
			<TableHead>
				<TableHeadCell>Email</TableHeadCell>
				<TableHeadCell>Active</TableHeadCell>
				<TableHeadCell>Verified</TableHeadCell>
				<TableHeadCell>Researcher</TableHeadCell>
				<TableHeadCell>Full data access</TableHeadCell>
				<TableHeadCell>Research Code</TableHeadCell>
				<TableHeadCell>Admin</TableHeadCell>
				<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
			</TableHead>
			<TableBody>
				{#each users as user (user.id)}
					<TableBodyRow>
						<TableBodyCell>
							{user.email}
						</TableBodyCell>
						<TableBodyCell>
							<Checkbox bind:checked={user.is_active} onchange={() => {saveDisabled[user.id]=false}} />
						</TableBodyCell>
						<TableBodyCell>
							<Checkbox bind:checked={user.is_verified} onchange={() => {saveDisabled[user.id]=false}} />
						</TableBodyCell>
						<TableBodyCell>
							<Checkbox bind:checked={user.is_researcher} onchange={() => {saveDisabled[user.id]=false}} />
						</TableBodyCell>
						<TableBodyCell>
							<Checkbox bind:checked={user.full_data_access} onchange={() => {saveDisabled[user.id]=false}} />
						</TableBodyCell>
						<TableBodyCell>
							{#if user.research_group_id > 0}
							<Alert border={user.is_researcher} color="dark">
								{user.research_group_id}
							</Alert>
								{:else if user.is_researcher}
								<Button onclick={() => {addResearchGroup(user)}}>Add research code</Button>
							{/if}
						</TableBodyCell>
						<TableBodyCell>
							<Checkbox bind:checked={user.is_superuser} onchange={() => {saveDisabled[user.id]=false}} />
						</TableBodyCell>
						<TableBodyCell>
							<SaveButton disabled={saveDisabled[user.id]} onclick={() => {updateUser(user)}} />
						</TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Table>
	</div>
</Card>
