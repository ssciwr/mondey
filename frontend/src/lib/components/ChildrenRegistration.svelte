<svelte:options runes={true} />

<script lang="ts">
import {
	type ChildAnswerPublic,
	type ChildCreate,
	type ChildPublic,
	type ErrorModel,
	type GetChildQuestionsResponse,
	createChild,
	deleteChild,
	deleteChildImage,
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
import { i18n } from "$lib/i18n.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activeTabChildren, componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import { Button, Card, Heading, Hr, Input, Spinner } from "flowbite-svelte";
import {
	CheckCircleOutline,
	PlayOutline,
	TrashBinOutline,
	UserSettingsOutline,
} from "flowbite-svelte-icons";

// questions and answers about child that are not part of the child object
let questionnaire: GetChildQuestionsResponse = $state(
	[] as GetChildQuestionsResponse,
);
let answers: { [k: number]: ChildAnswerPublic } = $state({});

// data for the child object
let {
	name = $bindable(null),
	image = $bindable(null),
	color = $bindable("#ffffff"),
	birthyear = $bindable(null),
	birthmonth = $bindable(null),
}: {
	name: string | null | undefined;
	image: File | boolean | null;
	color: string;
	birthyear: number | null;
	birthmonth: number | null;
} = $props();

// functionality
let disableEdit: boolean = $state(false);
let disableImageDelete: boolean = $state(false);
let imageDeleted: boolean = $state(false);
let alertMessage: string = $state(i18n.tr.childData.alertMessageMissing);
let showAlert = $state(false);
let childLabel = $derived(name ? name : i18n.tr.childData.newChildHeadingLong);
let breadcrumbdata = $derived([
	{
		label: childLabel,
		symbol: UserSettingsOutline,
	},
]);

let promise = $state(setup());

async function setup(): Promise<{
	questionnaire: GetChildQuestionsResponse;
	answers: { [k: string]: ChildAnswerPublic };
}> {
	await currentChild.load_data();

	// get questions
	const questions = await getChildQuestions();
	if (questions.error || questions.data === undefined) {
		console.log(
			"Error when getting userquestions: ",
			(questions.error as ErrorModel).detail,
		);
		showAlert = true;
		alertMessage = i18n.tr.childData.alertMessageError;
	} else {
		questionnaire = questions.data;
	}

	if (currentChild.id !== null) {
		const child = await getChild({ path: { child_id: currentChild.id } });

		if (child.error) {
			console.log("Error when getting child: ", child.error.detail);
			showAlert = true;
			alertMessage = i18n.tr.childData.alertMessageError;
		} else {
			name = child.data.name ?? null;
			birthyear = child.data.birth_year;
			birthmonth = child.data.birth_month;
			image = child.data.has_image ? true : null;
			color = child.data.color;
		}

		// get existing answers
		let currentAnswers = await getCurrentChildAnswers({
			path: {
				child_id: currentChild.id,
			},
		});

		if (currentAnswers?.error || currentAnswers.data === undefined) {
			console.log(
				"Error when getting current answers for child: ",
				currentAnswers.error.detail,
			);
			showAlert = true;
			alertMessage = i18n.tr.childData.alertMessageError;
		} else {
			answers = currentAnswers.data;
			disableEdit = true;
		}
	}

	// DEBUG/TEMPORARY: when we have no answers for existing questions,
	// we need to create empty
	// ones that bind to the form. this might not be necessary in the final
	// version b/c it only can happen when the admin changes questions on the
	// fly in the database. Doing so should eventually elicit database
	// migration though, which should assure consistency
	for (const question of questionnaire) {
		if (answers[question.id] === undefined) {
			answers[question.id] = {
				question_id: question.id,
				answer: "",
				additional_answer: "",
			};
		}
	}
	console.log("setup done");
	return { questionnaire: questionnaire, answers: answers };
}

async function submitChildData(): Promise<void> {
	if (currentChild.id === null) {
		// make new child if we don´t have one already
		const new_child = await createChild({
			body: {
				name: name,
				birth_year: birthyear,
				birth_month: birthmonth,
				has_image: image !== null,
				color: image !== null ? null : color,
			} as ChildCreate,
		});

		if (new_child.error) {
			showAlert = true;
			alertMessage =
				i18n.tr.childData.alertMessageCreate + new_child.error.detail;
			return;
		}
		currentChild.id = new_child.data.id;
	} else {
		console.log("updating existing child");

		// update existing child
		const response = await updateChild({
			body: {
				name: name,
				birth_year: birthyear,
				birth_month: birthmonth,
				id: currentChild.id,
				has_image: image !== null && imageDeleted === false,
				color: color,
			} as ChildPublic,
		});

		if (response.error) {
			showAlert = true;
			alertMessage = `${i18n.tr.childData.alertMessageUpdate} ${response.error.detail}`;
			return;
		}
	}

	// send answers to changeable questions
	const response = await updateCurrentChildAnswers({
		body: answers,
		path: {
			child_id: currentChild.id,
		},
	});

	if (response.error) {
		console.log(
			"Error when sending user question answers: ",
			response.error.detail,
		);
		alertMessage = `${i18n.tr.childData.alertMessageError} ${response.error.detail}`;
		showAlert = true;
		return;
	}
}

async function submitImageData(): Promise<void> {
	if (currentChild.id === null) {
		console.log("no child id, no image to upload");
		showAlert = true;
		alertMessage = i18n.tr.childData.alertMessageError;
		return;
	}

	if (imageDeleted === true) {
		const response = await deleteChildImage({
			path: {
				child_id: currentChild.id,
			},
		});

		if (response.error) {
			console.log("error during file delete: ", response.error.detail);
			showAlert = true;
			alertMessage = `${i18n.tr.childData.alertMessageUpdate} ${response.error.detail}`;
			return;
		}
	} else if (image instanceof File && imageDeleted === false) {
		const response = await uploadChildImage({
			body: {
				file: image,
			},
			path: {
				child_id: currentChild.id,
			},
		});

		if (response.error) {
			console.log("error during file upload: ", response.error.detail);
			showAlert = true;
			alertMessage = `${i18n.tr.childData.alertMessageError} ${response.error.detail}`;
			return;
		}
	} else {
		// DEBUG/TEMPORARY: this should never happen in the final version
		console.log("do nothing with image: ", imageDeleted, image, typeof image);
	}
}

async function submitData(): Promise<void> {
	// submit child data
	await submitChildData();

	// handle image data
	await submitImageData();

	// disable all elements to make editing a conscious choice amd go back to childrenGallery
	console.log("submission of child data successful.");
	activeTabChildren.set("childrenGallery");
}
</script>

{#if i18n.locale}
<Breadcrumbs data={breadcrumbdata} />
{#await promise}
<div class = "flex justify-center items-center ">
<Spinner /> <p>{i18n.tr.childData.loadingMessage}</p>
</div>
{:then { questionnaire, answers }}
	{#if showAlert}
		<AlertMessage
			title={i18n.tr.childData.alertMessageTitle}
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
						title={i18n.tr.childData.alertMessageTitle}
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
						label={i18n.tr.childData.childName}
						required={true}
						placeholder={i18n.tr.childData.pleaseEnter}
						disabled={disableEdit}
						id="child_name"
						kwargs = {{type: "text"}}
						/>

					<DataInput
						component={componentTable["input"]}
						bind:value={birthmonth}
						label={i18n.tr.childData.childBirthMonth}
						required={true}
						placeholder={i18n.tr.childData.pleaseEnterNumber}
						disabled={disableEdit}
						id="child_birthmonth"
						kwargs = {{type: "number", min: 0, max:12, step: '1'}}
						/>

					<DataInput
						component={componentTable["input"]}
						bind:value={birthyear}
						label={i18n.tr.childData.childBirthYear}
						required={true}
						placeholder={i18n.tr.childData.pleaseEnterNumber}
						disabled={disableEdit}
						id="child_birthyear"
						kwargs = {{type: "number", min: 2007, step: '1'}}
						/>

					<DataInput
						component={componentTable["fileupload"]}
						bind:value={image}
						label={image !== null ? i18n.tr.childData.imageOfChildChange : i18n.tr.childData.imageOfChildNew}
						required={false}
						placeholder={i18n.tr.childData.noFileChosen}
						disabled={disableEdit}
						id="child_image"
						kwargs = {{accept: ".jpg, .jpeg, .png", clearable: true}}
						/>

					<DataInput
						component={Input}
						bind:value={color}
						label={i18n.tr.childData.childColor}
						required={false}
						placeholder={i18n.tr.childData.chooseColor}
						disabled={disableEdit}
						id="child_color"
						kwargs = {{type: "color"}}
						componentClass="w-1/4 h-12 rounded"
					/>

					{#if image !== null && disableEdit === false}
						<Button
							type="button"
							class="w-full text-center text-sm text-white"
							color={"red"}
							disabled={disableImageDelete}
							on:click={() => {
								image = null;
								disableImageDelete = true;
								imageDeleted = true;
							}}
						>
							<div class="flex items-center justify-center">
								<TrashBinOutline size='md'/> {i18n.tr.childData.deleteImageButton}
							</div>
						</Button>
					{:else if disableImageDelete === true}
						<p class="text-center text-sm text-gray-700 dark:text-gray-400 flex items-center justify-center">
							<CheckCircleOutline size="lg" color="green"/> {i18n.tr.childData.imageOfChildChangeDelete}
						</p>
					{/if}

					{#each questionnaire as element, i}
						<DataInput
							component={element.component ? componentTable[element.component] : undefined}
							bind:value={answers[element.id].answer}
							bind:additionalValue={answers[element.id]
								.additional_answer}
							label={element?.text?.[i18n.locale].question}
							textTrigger={element.additional_option}
							required={element.component === 'fileupload' ? false : true}
							additionalRequired={true}
							id={"input_" + String(i)}
							items={element?.text?.[i18n.locale].options_json === ""
								? undefined
								: JSON.parse(
										element?.text?.[i18n.locale].options_json ?? '',
									)}
							disabled={disableEdit}
							placeholder=""
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
								{i18n.tr.childData.changeData}
							</div>
						</Button>
					{:else}
						<Button
							class="dark:bg-primay-700 w-full bg-primary-700 text-center text-sm text-white hover:bg-primary-800 hover:text-white dark:hover:bg-primary-800"
							type="submit"
							>{i18n.tr.childData.submitButtonLabel}</Button
						>
					{/if}
					{#if currentChild.id !== null}
						<Button
							class=" w-full text-center text-sm text-white"
							type="button"
							color="green"
							on:click={() => {
								activeTabChildren.set("milestoneGroup");
							}}
							>
							<PlayOutline size='sm'/>
							{i18n.tr.childData.nextButtonLabel}
						</Button>
						<Button
							class=" w-full text-center text-sm text-white"
							color = "yellow"
							type ="button"
							onclick={() => {
								activeTabChildren.set("childrenFeedback");
							}}
							>
							<PlayOutline size='sm'/>
							{i18n.tr.childData.feedbackButtonLabel}
						</Button>
						<Hr hrClass="my-8"/>
						<Button
							class=" w-full text-center text-sm text-white"
							type="button"
							color="red"
							on:click={async () => {
								if (currentChild.id === null) {
									console.log("no child id, no child to delete");
									showAlert = true;
									alertMessage = i18n.tr.childData.alertMessageError;
									return;
								}

								const response = await deleteChild({
									path: {
										child_id: currentChild.id,
									}
								});

								if (response.error) {
									console.log("Error when deleting child");
									showAlert = true;
									alertMessage=i18n.tr.childData.alertMessageError + response.error.detail;
								}
								else {
									activeTabChildren.update((value) => {
										return "childrenGallery";
									});
									currentChild.id = null;
								}
							}}
							><TrashBinOutline size='sm'/> {i18n.tr.childData.deleteButtonLabel}</Button
						>
					{/if}
				</form>
			</Card>
		</div>
	{/if}
{:catch error}
	<AlertMessage
		title={i18n.tr.childData.alertMessageTitle}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
{:else}
	<AlertMessage
		title={i18n.tr.childData.alertMessageTitle}
		message={i18n.tr.childData.alertMessageError}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/if}
