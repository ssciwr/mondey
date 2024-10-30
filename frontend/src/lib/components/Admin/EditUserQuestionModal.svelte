<svelte:options runes={true} />

<script lang="ts">
import { refreshUserQuestions } from "$lib/admin.svelte";
import { updateUserQuestion } from "$lib/client/services.gen";
import type { UserQuestionAdmin } from "$lib/client/types.gen";
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
	userQuestion,
}: { open: boolean; userQuestion: UserQuestionAdmin | undefined } = $props();

let preview_lang = $state("de");
let preview_answer = $state("");

// FIXME: use the componentTable here
const inputTypes: Array<SelectOptionType<string>> = [
	{ value: "text", name: "text" },
	{ value: "select", name: "select" },
];

function updateOptionsJson() {
	if (!userQuestion) {
		return;
	}
	const values = userQuestion.options.split(";");
	for (const lang_id of $locales) {
		const items = userQuestion.text[lang_id].options.split(";");
		userQuestion.text[lang_id].options_json = JSON.stringify(
			values.map((value, index) => ({ value: value, name: items[index] })),
		);
	}
}

async function saveChanges() {
	if (!userQuestion) {
		return;
	}
	const { data, error } = await updateUserQuestion({ body: userQuestion });
	if (error) {
		console.log(error);
	} else {
		console.log(data);
		await refreshUserQuestions();
	}
}
</script>

<Modal title="Edit user question" bind:open autoclose size="xl">
	{#if userQuestion}
		<div class="flex flex-row items-center">
			<div class="mr-5 grow">
				<div class="mb-5">
					<Label class="mb-2">{$_('admin.question')}</Label>
					{#each Object.values(userQuestion.text) as text}
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<InputAddon>{text.lang_id}</InputAddon>
								<Input
									bind:value={text.question}
									on:input={() => {
										userQuestion = userQuestion;
									}}
									placeholder={$_('admin.placeholder')}
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
						bind:value={userQuestion.component}
						placeholder=""
					/>
				</div>
				{#if userQuestion.component === 'select'}
					<div class="mb-5">
						<Label class="mb-2">Options</Label>
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<InputAddon>Option values</InputAddon>
								<Textarea
									bind:value={userQuestion.options}
									on:input={updateOptionsJson}
									placeholder="Option values"
								/>
							</ButtonGroup>
						</div>
						{#each Object.values(userQuestion.text) as text}
							{console.log('text: ', text)}
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
									bind:value={userQuestion.additional_option}
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
							<InputPreview data={userQuestion} lang={preview_lang} bind:answer={preview_answer} />
						</Card>
						<Label class="mb-2">Generated answer:</Label>
						<Badge large border color="dark">{preview_answer}</Badge>
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
