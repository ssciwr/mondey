<svelte:options runes={true} />

<script lang="ts">
import {
	Table,
	TableBody,
	TableBodyCell,
	TableBodyRow,
	TableHead,
	TableHeadCell,
} from "flowbite-svelte";

import {
	createChild,
	createChildQuestion,
	createUserQuestion,
	deleteChildQuestion,
	deleteUserQuestion,
	orderChildQuestionsAdmin,
	orderUserQuestionsAdmin,
} from "$lib/client/sdk.gen";
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
import DangerousDeleteModal from "$lib/components/DangerousDeleteModal.svelte";
import { i18n } from "$lib/i18n.svelte";
import { childQuestions, userQuestions } from "$lib/stores/adminStore.svelte";
import { onMount } from "svelte";
import AlertMessage from "../AlertMessage.svelte";

let currentQuestion = $state(
	undefined as UserQuestionAdmin | ChildQuestionAdmin | undefined,
);
let currentQuestionId = $state(null as number | null);
let showEditQuestionModal = $state(false);
let showDeleteModal = $state(false);
let { kind }: { kind: "user" | "child" } = $props();
let currentOrderItems = $state([] as Array<{ id: number; text: string }>);
let showOrderItemsModal = $state(false);

let create: typeof createUserQuestion | typeof createChildQuestion =
	$state(createUserQuestion);
let doDelete: typeof deleteUserQuestion | typeof deleteChildQuestion =
	$state(deleteUserQuestion);
let build = $derived.by(() => {
	return (dry_run = true) => {
		return {
			path: { [`${kind}_question_id`]: currentQuestionId },
			query: { dry_run: dry_run },
		};
	};
});
let order: typeof orderUserQuestionsAdmin | typeof orderChildQuestionsAdmin =
	$state(orderUserQuestionsAdmin);
let questions: typeof userQuestions | typeof childQuestions =
	$state(userQuestions);

if (kind === "child") {
	create = createChildQuestion;
	doDelete = deleteChildQuestion;
	order = orderChildQuestionsAdmin;
	questions = childQuestions;
} else if (kind !== "user") {
	console.log("Error, kind must be 'user' or 'child', currently is", kind);
}

async function addQuestion() {
	const { data, error } = await create();
	if (error) {
		console.log(error);
		currentQuestion = undefined;
	} else {
		await questions.refresh();
		currentQuestion = data;
		showEditQuestionModal = true;
	}
}

function doDeleteQuestion(dry_run = true) {
	if (!currentQuestionId) {
		return;
	}
	return doDelete(build(dry_run));
}

onMount(async () => {
	await questions.refresh();
});
</script>

{#if i18n.locale}
<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">
	{i18n.tr.admin[`${kind}Questions`]}
	<ReorderButton
			onclick={() => {
						currentOrderItems = questions.data.map((question) => {return {id: question.id, text: question?.text?.[i18n.locale]?.question ?? ''};});
						showOrderItemsModal = true;
					}}
	/>
</h3>
<Table>
	<TableHead>
		<TableHeadCell>Question</TableHeadCell>
		<TableHeadCell>Input type</TableHeadCell>
		<TableHeadCell>{i18n.tr.admin.actions}</TableHeadCell>
	</TableHead>
	<TableBody>
		{#each questions.data as question, groupIndex (question.id)}
			<TableBodyRow>
				<TableBodyCell>
					{question?.text?.[i18n.locale]?.question}
				</TableBodyCell>
				<TableBodyCell>
					{question?.component}
				</TableBodyCell>
				<TableBodyCell>
					<EditButton
						onclick={() => {
							currentQuestion = questions.data[groupIndex];
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
			<TableBodyCell>
				<AddButton onclick={addQuestion} />
			</TableBodyCell>
		</TableBodyRow>
	</TableBody>
</Table>

{#key showEditQuestionModal}
	<EditQuestionModal
		{kind}
		bind:open={showEditQuestionModal}
		question={currentQuestion}
	/>
{/key}
<DangerousDeleteModal bind:open={showDeleteModal}
					  deleteDryRunnableRequest={doDeleteQuestion}
					  afterDelete={questions.refresh}
					  intendedConfirmCode={i18n.tr.admin.delete}
/>

<OrderItemsModal bind:open={showOrderItemsModal} items={currentOrderItems} endpoint={order} callback={questions.refresh}/>
{:else}
	<AlertMessage title={i18n.tr.userData.alertMessageTitle} message={i18n.tr.userData.alertMessageError} />
{/if}
