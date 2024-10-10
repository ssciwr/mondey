<svelte:options runes={true} />

<script lang="ts">
	import {
		Button,
		Badge,
		Card,
		InputAddon,
		Textarea,
		Input,
		Label,
		ButtonGroup,
		Modal,
		Select,
		type SelectOptionType
	} from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';
	import { languages } from '$lib/stores/langStore';
	import { updateUserQuestion } from '$lib/client/services.gen';
	import InputPreview from '$lib/components/Admin/InputPreview.svelte';
	import SaveButton from '$lib/components/Admin/SaveButton.svelte';
	import CancelButton from '$lib/components/Admin/CancelButton.svelte';
	import type { UserQuestionAdmin } from '$lib/client/types.gen';
	import { refreshUserQuestions } from '$lib/admin.svelte';

	let {
		open = $bindable(false),
		userQuestion
	}: { open: boolean; userQuestion: UserQuestionAdmin | undefined } = $props();

	let preview_lang_id = $state('1');
	let preview_answer = $state('');

	const inputTypes: Array<SelectOptionType<string>> = [
		{ value: 'text', name: 'text' },
		{ value: 'select', name: 'select' }
	];

	function updateOptionsJson() {
		if (!userQuestion) {
			return;
		}
		const values = userQuestion.options.split(';');
		for (const lang_id in $languages) {
			const items = userQuestion.text[lang_id].options.split(';');
			userQuestion.text[lang_id].options_json = JSON.stringify(
				values.map(function (value, index) {
					return { value: value, name: items[index] };
				})
			);
		}
	}

	export async function saveChanges() {
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
								<InputAddon>{$languages[text.lang_id]}</InputAddon>
								<Input
									bind:value={text.question}
									on:input={() => {
										userQuestion = userQuestion;
									}}
									placeholder={$_('admin.question')}
								/>
							</ButtonGroup>
						</div>
					{/each}
				</div>
				<div class="mb-5">
					<Label class="mb-2">Input type</Label>
					<Select class="mt-2" items={inputTypes} bind:value={userQuestion.input} placeholder="" />
				</div>
				{#if userQuestion.input === 'select'}
					<div class="mb-5">
						<Label class="mb-2">Options</Label>
						<div class="mb-1">
							<ButtonGroup class="w-full">
								<InputAddon>name</InputAddon>
								<Textarea
									bind:value={userQuestion.options}
									on:input={updateOptionsJson}
									placeholder="Option names"
								/>
							</ButtonGroup>
						</div>
						{#each Object.values(userQuestion.text) as text}
							<div class="mb-1">
								<ButtonGroup class="w-full">
									<InputAddon>{$languages[text.lang_id]}</InputAddon>
									<Textarea
										bind:value={text.options}
										on:input={updateOptionsJson}
										placeholder="Options"
									/>
								</ButtonGroup>
							</div>
						{/each}
					</div>
				{/if}
			</div>
			<div>
				<Card>
					<div class="mb-5">
						<Label class="mb-2">Preview</Label>
						<div class="flex flex-row">
							<ButtonGroup class="mb-2 mr-2">
								{#each Object.entries($languages) as [lang, lang_id]}
									<Button
										checked={preview_lang_id === lang_id}
										on:click={(e) => {
											e.stopPropagation();
											preview_lang_id = lang_id;
										}}>{lang}</Button
									>
								{/each}
							</ButtonGroup>
						</div>
						<Card class="mb-4 bg-blue-300">
							<InputPreview
								data={userQuestion}
								lang_id={preview_lang_id}
								bind:answer={preview_answer}
							/>
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
