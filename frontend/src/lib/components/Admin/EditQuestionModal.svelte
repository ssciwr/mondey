<svelte:options runes={true} />

<script lang="ts">
import { refreshChildQuestions, refreshUserQuestions } from "$lib/admin.svelte";
import {
	updateChildQuestion,
	updateUserQuestion,
} from "$lib/client/services.gen";
import type {
	ChildQuestionAdmin,
	UserQuestionAdmin,
} from "$lib/client/types.gen";
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import InputPreview from "$lib/components/Admin/InputPreview.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import {
	Badge,
	Button,
	ButtonGroup,
	Card,
	Input,
	InputAddon,
	Label,
	Modal,
	Select,
	type SelectOptionType,
	Textarea,
} from "flowbite-svelte";
import { _, locales } from "svelte-i18n";

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
let update: any;
let refresh: any;

if (kind === "user") {
	update = updateUserQuestion;
	refresh = refreshUserQuestions;
} else if (kind === "child") {
	update = updateChildQuestion;
	refresh = refreshChildQuestions;
} else {
	console.log(
		"Error, kind must be either 'user' or 'child', currently is: ",
		kind,
	);
}

const inputTypes: Array<SelectOptionType<string>> = [
	{ value: "textarea", name: "text" },
	{ value: "select", name: "select" },
	{ value: "date", name: "date" },
];

function updateOptionsJson() {
	if (!question) {
		return;
	}
	const values = question.options.split(";");
	for (const lang_id of $locales) {
		const items = question.text[lang_id].options.split(";");
		question.text[lang_id].options_json = JSON.stringify(
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

<Modal title="Edit user question" bind:open autoclose size="xl">
	{#if question}
		<div class="flex flex-row items-center">
			<div class="mr-5 grow">
				<div class="mb-5">
					<Label class="mb-2">{$_("admin.question")}</Label>
					{#each Object.values(question.text) as text}
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<InputAddon>{text.lang_id}</InputAddon>
								<Input
									bind:value={text.question}
									on:input={() => {
										question = question;
									}}
									placeholder={$_("admin.placeholder")}
								/>
							</ButtonGroup>
						</div>
					{/each}
				</div>
				<div class="mb-5">
					<Label class="mb-2">Input type</Label>
					<Select
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
								<InputAddon>Option values</InputAddon>
								<Textarea
									bind:value={question.options}
									on:input={updateOptionsJson}
									placeholder="Option values"
								/>
							</ButtonGroup>
						</div>
						{#each Object.values(question.text) as text}
							{console.log("text: ", text)}
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
						<Label class="mb-2">Additional Option</Label>
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<Textarea
									bind:value={question.additional_option}
									placeholder="Displayed additional option"
								/>
							</ButtonGroup>
						</div>
					</div>
				{/if}
			</div>
			<div>
				<Card>
					<div class="mb-5">
						<Label class="mb-2">Preview</Label>
						<div class="flex flex-row">
							<ButtonGroup class="mb-2 mr-2">
								{#each $locales as lang_id}
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
							<InputPreview
								data={question}
								lang={preview_lang}
								bind:answer={preview_answer}
							/>
						</Card>
						<Label class="mb-2">Generated answer:</Label>
						<Badge large border color="dark">{preview_answer}</Badge
						>
					</div>
				</Card>
			</div>
		</div>
	{/if}
	<svelte:fragment slot="footer">
		<SaveButton onclick={saveChanges} />
		<CancelButton />
	</svelte:fragment>
</Modal>
