<svelte:options runes={true} />

<script lang="ts">
import { updateChildQuestion, updateUserQuestion } from "$lib/client/sdk.gen";
import type {
	ChildQuestionAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import InputPreview from "$lib/components/Admin/InputPreview.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import { childQuestions, userQuestions } from "$lib/stores/adminStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Badge,
	Button,
	ButtonGroup,
	Card,
	Checkbox,
	Input,
	InputAddon,
	Label,
	Modal,
	Select,
	type SelectOptionType,
	Textarea,
} from "flowbite-svelte";

let {
	open = $bindable(false),
	question,
	kind,
}: {
	open: boolean;
	question: UserQuestionAdmin | ChildQuestionAdmin | undefined;
	kind: string;
} = $props();
let preview_lang = $state("de");
let preview_answer = $state("");
let options = $derived.by(() => {
	let opts = [{ value: "", name: "No free text option" }];
	if (!question || !question.options) {
		return opts;
	}
	return opts.concat(
		question.options
			.replace(/;$/, "")
			.split(";")
			.map((value) => ({
				value: value,
				name: value,
			})),
	);
});
let update: any;
let refresh: any;
let questionsStore: typeof userQuestions | typeof childQuestions =
	$state(userQuestions);

if (kind === "user") {
	update = updateUserQuestion;
	refresh = userQuestions.refresh;
	questionsStore = userQuestions;
} else if (kind === "child") {
	update = updateChildQuestion;
	refresh = childQuestions.refresh;
	questionsStore = childQuestions;
} else {
	console.log(
		"Error, kind must be either 'user' or 'child', currently is: ",
		kind,
	);
}

const inputTypes: Array<SelectOptionType<string>> = [
	{ value: "textarea", name: "Text" },
	{ value: "select", name: "Multiple Choice" },
];

// candidate parent questions: other multiple-choice questions of the same
// kind (a question can only depend on the answer to a select question)
let parentQuestions = $derived(
	questionsStore.data.filter(
		(q) => q.id !== question?.id && q.component === "select",
	),
);
let parentQuestionOptions = $derived([
	{ value: null, name: i18n.tr.admin.questionDependencyNone },
	...parentQuestions.map((q) => ({
		value: q.id,
		name: q?.text?.[preview_lang]?.question || q.name || `Question ${q.id}`,
	})),
]);
let selectedParent = $derived(
	question?.depends_on_question_id == null
		? undefined
		: parentQuestions.find(
				(q) => q.id === Number(question?.depends_on_question_id),
			),
);
// the option values of the selected parent question that can trigger showing
// this question
let parentAnswerOptions = $derived(
	(selectedParent?.options ?? "")
		.replace(/;$/, "")
		.split(";")
		.filter((value) => value !== ""),
);
let showIfAnswerValues = $derived(
	(question?.show_if_answer ?? "").split(";").filter((value) => value !== ""),
);

function toggleShowIfAnswer(value: string, checked: boolean) {
	if (!question) {
		return;
	}
	const values = new Set(showIfAnswerValues);
	if (checked) {
		values.add(value);
	} else {
		values.delete(value);
	}
	question.show_if_answer = [...values].join(";");
}

function clearShowIfAnswer() {
	if (question) {
		question.show_if_answer = "";
	}
}

function updateOptionsJson() {
	if (!question || !question.options || !question.text) {
		return;
	}
	const values = question.options.split(";");
	for (const lang_id of i18n.locales) {
		const text = question.text[lang_id];
		if (!text?.options) {
			continue;
		}
		const items = text.options.split(";");
		text.options_json = JSON.stringify(
			values.map((value, index) => ({
				value: value,
				name: items[index],
			})),
		);
	}
}

async function saveChanges() {
	if (!question) {
		return;
	}
	// keep dependency fields consistent: no parent => no trigger values
	if (question.depends_on_question_id == null) {
		question.depends_on_question_id = null;
		question.show_if_answer = "";
	}
	const { data, error } = await update({
		body: question,
	});
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await refresh();
	}
}
</script>

<style>
	:global(.modal-scrollable) {
		display: flex !important;
		align-items: flex-start !important;
		padding-top: 2rem;
		margin-bottom:10rem!important;
	}

	:global(.modal-scrollable > div) {
		max-height: calc(100vh - 4rem);
		overflow-y: auto;
	}
</style>

<Modal title="Edit user question" class="modal-scrollable" bind:open autoclose >
	{#if question && question.text}
		<div>
			<div class="flex flex-row items-center">
				<div class="mr-5 grow">
					<div class="mb-5">
						<Label class="mb-2">{i18n.tr.admin.name}</Label>
						<Input bind:value={question.name} placeholder={i18n.tr.admin.name}/>
					</div>
					<div class="mb-5">
						<Label class="mb-2">{i18n.tr.admin.question}</Label>
						{#each Object.values(question.text) as text}
							<div class="mb-1">
								<ButtonGroup class="w-full">
									<InputAddon>{text.lang_id}</InputAddon>
									<Input
										data-testid={`text-question-input-${text.lang_id}`}
										bind:value={text.question}
										placeholder=""
									/>
								</ButtonGroup>
							</div>
						{/each}
					</div>
					<div class="mb-5">
						<Label class="mb-2">Input type</Label>
						<Select
							data-testid="questionTypeSelect"
							class="mt-2"
							items={inputTypes}
							bind:value={question.component}
							placeholder=""
						/>
					</div>
					{#if question.component === "select"}
						<div class="mb-5">
							<Label class="mb-2">Options</Label>
							<div class="mb-1">
								<ButtonGroup class="w-full">
									<InputAddon>Option values (separate with ";" - like "Option A;Option B")</InputAddon>
									<Textarea
										bind:value={question.options}
										on:input={updateOptionsJson}
										placeholder="Option values"
									/>
								</ButtonGroup>
							</div>
							{#each Object.values(question.text) as text}
								<div class="mb-1">
									<ButtonGroup class="w-full">
										<InputAddon>{text.lang_id}</InputAddon>
										<Textarea
											bind:value={text.options}
											on:input={updateOptionsJson}
											placeholder="Displayed options"
										/>
									</ButtonGroup>
								</div>
							{/each}
							<div class="mb-1">
							<Label class="mb-2">Free text Option</Label>
							<Select
									class="mt-2"
									items={options}
									bind:value={question.additional_option}
									placeholder=""
							/>
							</div>
						</div>
					{/if}
					<Label class="mb-2">{i18n.tr.admin.required}</Label>
					<div class="mb-1">
						<ButtonGroup class="w-full">
							<Checkbox
									bind:checked={question.required}
							/>
						</ButtonGroup>
					</div>
					<Label class="mb-2">{i18n.tr.admin.visibility}</Label>
					<div class="mb-1">
						<ButtonGroup class="w-full">
							<Checkbox data-testid="visibility-checkbox" bind:checked={question.visibility}></Checkbox>
						</ButtonGroup>
					</div>
					<div class="mb-5 mt-5">
						<Label class="mb-2">{i18n.tr.admin.questionDependency}</Label>
						<Select
							data-testid="dependsOnSelect"
							class="mt-2"
							items={parentQuestionOptions}
							bind:value={question.depends_on_question_id}
							onchange={clearShowIfAnswer}
							placeholder=""
						/>
					</div>
					{#if question.depends_on_question_id != null}
						<div class="mb-5">
							<Label class="mb-2">{i18n.tr.admin.questionDependencyAnswer}</Label>
							{#if parentAnswerOptions.length === 0}
								<p class="text-sm text-gray-500">
									{i18n.tr.admin.questionDependencyNoAnswerOptions}
								</p>
							{:else}
								{#each parentAnswerOptions as value}
									<div class="mb-1">
										<Checkbox
											checked={showIfAnswerValues.includes(value)}
											on:change={(e) =>
												toggleShowIfAnswer(
													value,
													(e.target as HTMLInputElement).checked,
												)}
										>{value}</Checkbox>
									</div>
								{/each}
							{/if}
						</div>
					{/if}
				</div>
				<div>
					<Card>
						<div class="mb-5">
							<Label class="mb-2">Preview</Label>
							<div class="flex flex-row">
								<ButtonGroup class="mb-2 mr-2">
									{#each i18n.locales as lang_id}
										<Button
											checked={preview_lang === lang_id}
											on:click={(e) => {
												e.stopPropagation();
												preview_lang = lang_id;
											}}>{lang_id}</Button
										>
									{/each}
								</ButtonGroup>
							</div>
							<Card class="mb-4 bg-blue-300">
								<InputPreview data={question} lang={preview_lang} bind:answer={preview_answer}/>
							</Card>
							<Label class="mb-2">Generated answer:</Label>
							<Badge large border color="dark">{preview_answer}</Badge
							>
						</div>
					</Card>
				</div>
			</div>
		</div>
	{/if}
	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges} />
		<CancelButton />
	</svelte:fragment>
</Modal>
