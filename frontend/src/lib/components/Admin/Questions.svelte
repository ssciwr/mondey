<svelte:options runes={true} />

<script lang="ts">
import {
	Card,
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";

import { refreshChildQuestions, refreshUserQuestions } from "$lib/admin.svelte";
import {
	createChildQuestion,
	createUserQuestion,
	deleteChildQuestion,
	deleteUserQuestion,
} from "$lib/client/services.gen";
import type {
	ChildQuestionAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import DeleteModal from "$lib/components/Admin/DeleteModal.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import EditQuestionModal from "$lib/components/Admin/EditQuestionModal.svelte";
import { childQuestions, userQuestions } from "$lib/stores/adminStore";
import { type Component, onMount } from "svelte";
import { _, locale } from "svelte-i18n";
import type { Writable } from "svelte/store";

let currentQuestion = $state(
	undefined as UserQuestionAdmin | ChildQuestionAdmin | undefined,
);
let currentQuestionId = $state(null as number | null);
let showEditQuestionModal = $state(false);
let showDeleteModal = $state(false);
let { kind }: { kind: string } = $props();
let create: any;
let doDelete: any;
let refresh: any;
let build: any;
let component: Component = EditQuestionModal;
let questions:
	| Writable<Array<UserQuestionAdmin>>
	| Writable<Array<ChildQuestionAdmin>> = $state();

if (kind === "user") {
	create = createUserQuestion;
	doDelete = deleteUserQuestion;
	refresh = refreshUserQuestions;
	build = () => {
		return {
			path: { user_question_id: currentQuestionId },
		};
	};
	questions = userQuestions;
} else if (kind === "child") {
	create = createChildQuestion;
	doDelete = deleteChildQuestion;
	refresh = refreshChildQuestions;
	build = () => {
		return {
			path: { child_question_id: currentQuestionId },
		};
	};
	questions = childQuestions;
} else {
	console.log("Error, kind must be 'user' or 'child', currently is", kind);
}

async function addQuestion() {
	const { data, error } = await create();
	if (error) {
		console.log(error);
		currentQuestion = undefined;
	} else {
		await refresh();
		currentQuestion = data;
		showEditQuestionModal = true;
	}
}

async function doDeleteQuestion() {
	if (!currentQuestionId) {
		return;
	}
	const { data, error } = await doDelete(build());
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await refresh();
	}
}

onMount(async () => {
	await refresh();
});
</script>

<Card size="xl" class="m-5 w-full">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
		{$_("admin.user-questions")}
	</h3>
	<Table>
		<TableHead>
			<TableHeadCell>Question</TableHeadCell>
			<TableHeadCell>Input type</TableHeadCell>
			<TableHeadCell>Options</TableHeadCell>
			<TableHeadCell>Actions</TableHeadCell>
		</TableHead>
		<TableBody>
			{#each $questions as question, groupIndex (question.id)}
				<TableBodyRow>
					<TableBodyCell>
						{question?.text[$locale]?.question}
					</TableBodyCell>
					<TableBodyCell>
						{question?.component}
					</TableBodyCell>
					<TableBodyCell>
						{question?.text[$locale]?.options}
					</TableBodyCell>
					<TableBodyCell>
						<EditButton
							onclick={() => {
								currentQuestion = $questions[groupIndex];
								showEditQuestionModal = true;
							}}
						/>
						<DeleteButton
							onclick={() => {
								currentQuestionId = question.id;
								showDeleteModal = true;
							}}
						/>
					</TableBodyCell>
				</TableBodyRow>
			{/each}
			<TableBodyRow>
				<TableBodyCell></TableBodyCell>
				<TableBodyCell></TableBodyCell>
				<TableBodyCell></TableBodyCell>
				<TableBodyCell>
					<AddButton onclick={addQuestion} />
				</TableBodyCell>
			</TableBodyRow>
		</TableBody>
	</Table>
</Card>

{#key showEditQuestionModal}
	<svelte:component
		this={component}
		{kind}
		bind:open={showEditQuestionModal}
		question={currentQuestion}
	/>
{/key}
<DeleteModal bind:open={showDeleteModal} onclick={doDeleteQuestion} />
