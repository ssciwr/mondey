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
	orderChildQuestionsAdmin,
	orderUserQuestionsAdmin,
} from "$lib/client/services.gen";
import type {
	ChildQuestionAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import EditQuestionModal from "$lib/components/Admin/EditQuestionModal.svelte";
import OrderItemsModal from "$lib/components/Admin/OrderItemsModal.svelte";
import ReorderButton from "$lib/components/Admin/ReorderButton.svelte";
import DeleteModal from "$lib/components/DeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { childQuestions, userQuestions } from "$lib/stores/adminStore";
import { onMount } from "svelte";
import type { Writable } from "svelte/store";
import AlertMessage from "../AlertMessage.svelte";

let currentQuestion = $state(
	undefined as UserQuestionAdmin | ChildQuestionAdmin | undefined,
);
let currentQuestionId = $state(null as number | null);
let showEditQuestionModal = $state(false);
let showDeleteModal = $state(false);
let { kind }: { kind: string } = $props();
let currentOrderItems = $state([] as Array<{ id: number; text: string }>);
let showOrderItemsModal = $state(false);

let create: any;
let doDelete: any;
let refresh: any = $state(undefined);
let build: any;
let order: any = $state(undefined);
let questions:
	| Writable<Array<UserQuestionAdmin>>
	| Writable<Array<ChildQuestionAdmin>> = $state(userQuestions);

if (kind === "user") {
	create = createUserQuestion;
	doDelete = deleteUserQuestion;
	refresh = refreshUserQuestions;
	build = () => {
		return {
			path: { user_question_id: currentQuestionId },
		};
	};
	order = orderUserQuestionsAdmin;
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
	order = orderChildQuestionsAdmin;
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

{#if i18n.locale}
<Card size="xl" class="m-5 w-full">
	<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
		{i18n.tr.admin[`${kind}Questions`]}
	</h3>
	<Table>
		<TableHead>
			<TableHeadCell>Question</TableHeadCell>
			<TableHeadCell>Input type</TableHeadCell>
			<TableHeadCell>Options</TableHeadCell>
			<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
		</TableHead>
		<TableBody>
			{#each $questions as question, groupIndex (question.id)}
				<TableBodyRow>
					<TableBodyCell>
						{question?.text[i18n.locale]?.question}
					</TableBodyCell>
					<TableBodyCell>
						{question?.component}
					</TableBodyCell>
					<TableBodyCell>
						{question?.text[i18n.locale]?.options}
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
					<ReorderButton
						onclick={() => {
							currentOrderItems = $questions.map((question) => {return {id: question.id, text: question.text[i18n.locale]?.question};});
							showOrderItemsModal = true;
						}}
					/>
				</TableBodyCell>
			</TableBodyRow>
		</TableBody>
	</Table>
</Card>

{#key showEditQuestionModal}
	<EditQuestionModal
		{kind}
		bind:open={showEditQuestionModal}
		question={currentQuestion}
	/>
{/key}
<DeleteModal bind:open={showDeleteModal} onclick={doDeleteQuestion} />

<OrderItemsModal bind:open={showOrderItemsModal} items={currentOrderItems} endpoint={order} callback={refresh}/>
{:else}
	<AlertMessage title={i18n.tr.userData.alertMessageTitle} message={i18n.tr.userData.alertMessageError} />
{/if}
