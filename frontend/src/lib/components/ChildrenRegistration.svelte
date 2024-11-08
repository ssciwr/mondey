<svelte:options runes={true} />

<script lang="ts">
import {
	type ChildAnswerPublic,
	type GetChildQuestionsResponse,
	createChild,
	deleteChild,
	getChild,
	getChildQuestions,
	getCurrentChildAnswers,
	updateChild,
	updateCurrentChildAnswers,
	uploadChildImage,
} from "$lib/client";
import AlertMessage from "$lib/components/AlertMessage.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { currentChild } from "$lib/stores/childrenStore";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading } from "flowbite-svelte";
import { _, locale } from "svelte-i18n";

// questions and answers about child that are not part of the child object
let questionnaire: GetChildQuestionsResponse = $state(
	[] as GetChildQuestionsResponse,
);
let answers: { [k: number]: ChildAnswerPublic } = $state({});

// data for the child object
let {
	name = $bindable(null),
	image = $bindable(null),
	birthyear = $bindable(null),
	birthmonth = $bindable(null),
}: {
	name: string | null | undefined;
	image: File | null;
	birthyear: string | null;
	birthmonth: string | null;
} = $props();

// functionality
let disableEdit: boolean = $state(false);
let alertMessage: string = $state($_("childData.alertMessageMissing"));
let showAlert = $state(false);
let promise = $state(setup());
let childLabel = $derived(name ? name : $_("childData.newChildHeadingLong"));

let breadcrumbdata = $derived([
	{
		label: $_("childData.overviewLabel"),
		onclick: () => {
			activeTabChildren.update((value) => {
				return "childrenGallery";
			});
		},
	},
	{
		label: childLabel,
	},
	{
		label: $_("milestone.milestones"),
		onclick: () => {
			activeTabChildren.set("milestoneOverview");
		},
	},
]);

async function setup(): Promise<{
	questionnaire: GetChildQuestionsResponse;
	answers: { [k: string]: ChildAnswerPublic };
}> {
	console.log("setup");
	// get questions
	const questions = await getChildQuestions();
	if (questions.error || questions.data === undefined) {
		console.log("Error when getting userquestions: ", questions.error.detail);
		showAlert = true;
		alertMessage = $_("childData.alertMessageError");
	} else {
		questionnaire = questions.data;
	}
	console.log("questionaire: ", questionnaire);

	if ($currentChild !== null) {
		const child = await getChild({ path: { child_id: $currentChild } });

		if (child.error) {
			console.log("Error when getting child: ", child.error.detail);
			showAlert = true;
			alertMessage = $_("childData.alertMessageError");
		} else {
			name = child.data.name;
			birthyear = String(child.data.birth_year);
			birthmonth = String(child.data.birth_month);
		}

		// get existing answers
		let currentAnswers = await getCurrentChildAnswers({
			path: {
				child_id: $currentChild,
			},
		});

		if (currentAnswers?.error || currentAnswers.data === undefined) {
			console.log(
				"Error when getting current answers for child: ",
				currentAnswers.error.detail,
			);
			showAlert = true;
			alertMessage = $_("childData.alertMessageError");
		} else {
			answers = currentAnswers.data;
			disableEdit = true;
		}
	} else {
		// create empty answers when creating a new child
		answers = questionnaire.reduce(
			(empty_answers, question) => {
				empty_answers[question.id] = {
					question_id: question.id,
					answer: "",
					additional_answer: "",
				};
				return empty_answers;
			},
			{} as { [k: number]: ChildAnswerPublic },
		);
	}
	console.log("setup done");

	return { questionnaire: questionnaire, answers: answers };
}

async function submitData(): Promise<void> {
	// make new child if we don´t have one already
	if ($currentChild === null) {
		const new_child = await createChild({
			body: {
				name: name,
				birth_year: birthyear,
				birth_month: birthmonth,
				has_image: image !== null,
			},
		});

		if (new_child.error) {
			showAlert = true;
			alertMessage =
				$_("childData.alertMessageCreate") + new_child.error.detail;
		} else {
			currentChild.set(new_child.data.id);
		}
	} else {
		const response = await updateChild({
			body: {
				name: name,
				birth_year: birthyear,
				birth_month: birthmonth,
				has_image: image !== null,
			},
		});

		if (response.error) {
			showAlert = true;
			alertMessage = $_("childData.alertMessageUpdate") + response.error.detail;
		}
	}

	if (image !== null) {
		const uploadResponse = await uploadChildImage({
			body: {
				file: image,
			},
			path: {
				child_id: $currentChild,
			},
		});

		if (uploadResponse.error) {
			console.log("error during file upload: ", uploadResponse.error.detail);
			showAlert = true;
			alertMessage =
				$_("childData.alertMessageError") + uploadResponse.error.detail;
		}
	}

	if ($currentChild) {
		// send answers to changeable questions
		const response = await updateCurrentChildAnswers({
			body: Object.values(answers),
			path: {
				child_id: $currentChild,
			},
		});

		if (response.error) {
			console.log(
				"Error when sending user question answers: ",
				response.error.detail,
			);
			alertMessage = $_("childData.alertMessageError");
			showAlert = true;
		} else {
			// disable all elements to make editing a conscious choice
			console.log("submission of child data successful.");
			disableEdit = true;
		}
	}
}
</script>

<Breadcrumbs data={breadcrumbdata} />
{#await promise}
	<p>{$_("childData.loadingMessage")}</p>
{:then { questionnaire, answers }}
	{#if showAlert}
		<AlertMessage
			title={$_("childData.alertMessageTitle")}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{:else}
		<div class="container m-2 mx-auto w-full pb-4">
			<Card class="container m-1 mx-auto w-full max-w-xl">
				<Heading
					tag="h3"
					class="m-1 mb-3 p-1 text-center font-bold tracking-tight text-gray-700 dark:text-gray-400"
					>{childLabel}</Heading
				>
				{#if showAlert}
					<AlertMessage
						title={$_("childData.alertMessageTitle")}
						message={alertMessage}
						onclick={() => {
							showAlert = false;
						}}
					/>
				{/if}
				<form
					class="m-1 mx-auto w-full flex-col space-y-6"
					onsubmit={preventDefault(submitData)}
				>
					<DataInput
						component={componentTable["input"]}
						bind:value={name}
						label={$_("childData.childName")}
						required={true}
						placeholder={$_("childData.pleaseEnter")}
						disabled={disableEdit}
						kwargs = {{type: "text"}}
						/>
					<DataInput
						component={componentTable["input"]}
						bind:value={birthmonth}
						label={$_("childData.childBirthMonth")}
						required={true}
						placeholder={$_("childData.pleaseEnterNumber")}
						disabled={disableEdit}
						kwargs = {{type: "number", min: 0, max:12, step: '1'}}
						/>
					<DataInput
						component={componentTable["input"]}
						bind:value={birthyear}
						label={$_("childData.childBirthYear")}
						required={true}
						placeholder={$_("childData.pleaseEnterNumber")}
						disabled={disableEdit}
						kwargs = {{type: "number", min: 2007, step: '1'}}
						/>

					<DataInput
						component={componentTable["fileupload"]}
						bind:value={image}
						label={$_("childData.imageOfChild")}
						required={true}
						placeholder={$_("childData.noFileChosen")}
						disabled={disableEdit}
						kwargs = {{accpet: ".jpg, .jpeg, .png"}}
						/>
					{#each questionnaire as element, i}
						<DataInput
							component={element.component ? componentTable[element.component] : undefined}
							bind:value={answers[element.id].answer}
							bind:additionalValue={answers[element.id]
								.additional_answer}
							label={element?.text[$locale].question}
							textTrigger={element.additional_option}
							required={element.component === 'fileupload' ? false : true}
							additionalRequired={true}
							id={"input_" + String(i)}
							items={element.text[$locale].options_json === ""
								? undefined
								: JSON.parse(
										element.text[$locale].options_json,
									)}
							disabled={disableEdit}
							placeholder={element.text[$locale].placeholder}
						/>
					{/each}
					{#if disableEdit === true}
						<Button
							type="button"
							class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
							on:click={() => {
								disableEdit = false;
							}}
						>
							<div class="flex items-center justify-center">
								{$_("childData.changeData")}
							</div>
						</Button>
					{:else}
						<Button
							class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
							type="submit"
							>{$_("childData.submitButtonLabel")}</Button
						>
					{/if}
					{#if $currentChild !== null}
						<Button
							class=" w-full text-center text-sm text-white"
							type="button"
							color="red"
							on:click={async () => {
								const response = await deleteChild({
									path: {
										child_id: $currentChild,
									}
								});

								if (response.error) {
									console.log("Error when deleting child");
									showAlert = true;
									alertMessage=$_("childData.alertMessageError") + response.error.detail;
								}
								else {
									activeTabChildren.update((value) => {
										return "childrenGallery";
									});
									currentChild.set(null);
								}
							}}
							>{$_("childData.deleteButtonLabel")}</Button
						>
					{/if}
				</form>
			</Card>
		</div>
	{/if}
{:catch error}
	<AlertMessage
		title={$_("childData.alertMessageTitle")}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
