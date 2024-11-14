<svelte:options runes={true} />

<script lang="ts">
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import {
	Card,
	Checkbox,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";

import { getUsers, usersPatchUser } from "$lib/client/services.gen";
import type { UserRead, UserUpdate } from "$lib/client/types.gen";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

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

onMount(async () => {
	await refreshUsers();
});
</script>

<Card size="xl" class="m-5 w-full">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
		{$_("admin.users")}
	</h3>
	<Table>
		<TableHead>
			<TableHeadCell>Email</TableHeadCell>
			<TableHeadCell>Active</TableHeadCell>
			<TableHeadCell>Verified</TableHeadCell>
			<TableHeadCell>Researcher</TableHeadCell>
			<TableHeadCell>Admin</TableHeadCell>
			<TableHeadCell>Actions</TableHeadCell>
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
						<Checkbox bind:checked={user.is_superuser} onchange={() => {saveDisabled[user.id]=false}} />
					</TableBodyCell>
					<TableBodyCell>
						<SaveButton disabled={saveDisabled[user.id]} onclick={() => {updateUser(user)}} />
					</TableBodyCell>
				</TableBodyRow>
			{/each}
		</TableBody>
	</Table>
</Card>
