<svelte:options runes={true} />

<script lang="ts">
import { goto } from "$app/navigation";
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
import DeleteButton from "$lib/components/Admin/DeleteButton.svelte";
import EditButton from "$lib/components/Admin/EditButton.svelte";
import DangerousDeleteModal from "$lib/components/DangerousDeleteModal.svelte";
import DataInput from "$lib/components/DataInput/DataInput.svelte";
import Breadcrumbs from "$lib/components/Navigation/Breadcrumbs.svelte";
import { displayChildImages } from "$lib/features";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { activePage, componentTable } from "$lib/stores/componentStore";
import { preventDefault } from "$lib/util";
import {
	Button,
	Card,
	Heading,
	Hr,
	Input,
	Spinner,
	Tooltip,
} from "flowbite-svelte";
import {
	ChartLineUpOutline,
	CheckCircleOutline,
	ClipboardCheckOutline,
	FlagOutline,
	GridPlusSolid,
	PenOutline,
	QuestionCircleSolid,
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
	color: string | null | undefined;
	birthyear: number | null;
	birthmonth: number | null;
} = $props();

// functionality
let disableEdit: boolean = $state(false);
let disableImageDelete: boolean = $state(false);
let showChildQuestions: boolean = $state(false);
let showDeleteModal: boolean = $state(false);
let imageDeleted: boolean = $state(false);
let childLabel = $derived(name ? name : i18n.tr.childData.newChildHeadingLong);
let breadcrumbdata = $derived([
	{
		label: i18n.tr.childData.overviewLabel,
		onclick: () => {
			goto("/userLand/children/gallery");
		},
		symbol: GridPlusSolid,
	},
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
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			i18n.tr.childData.alertMessageError,
			true,
		);
	} else {
		console.log("Set questionnaire");
		questionnaire = questions.data;
	}

	if (currentChild.id !== null) {
		console.log("Current child ID is: ", currentChild.id);
		const child = await getChild({ path: { child_id: currentChild.id } });

		if (child.error) {
			console.log("Error when getting child: ", child.error.detail);
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				i18n.tr.childData.alertMessageError,
				true,
			);
		} else {
			name = child.data.name ?? null;
			birthyear = child.data.birth_year;
			birthmonth = child.data.birth_month;
			image = child.data.has_image ? true : null;
			color = child.data.color ?? null;
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
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				i18n.tr.childData.alertMessageError,
				true,
			);
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
	return { questionnaire: questionnaire, answers: answers };
}

let birthmonthtext = $derived.by(() => {
	return birthmonth !== null
		? Intl.DateTimeFormat(i18n.locale || "en", { month: "long" }).format(
				new Date(birthmonth.toString()),
			)
		: "";
});

async function submitChildData(): Promise<void> {
	console.log("SubmitChild Data was called.");
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
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				i18n.tr.childData.alertMessageCreate + new_child.error.detail,
				true,
			);
			return;
		}
		currentChild.id = new_child.data.id;
	} else {
		console.log("updating existing child", currentChild.id);

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
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				`${i18n.tr.childData.alertMessageUpdate} ${response.error.detail}`,
				true,
			);
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
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			`${i18n.tr.childData.alertMessageError} ${response.error.detail}`,
			true,
		);
		return;
	}
}

async function submitImageData(): Promise<void> {
	if (false === displayChildImages) {
		console.warn("Image upload is manually disabled");
		return;
	}
	if (currentChild.id === null) {
		console.log("no child id, no image to upload");
		alertStore.showAlert(
			i18n.tr.childData.alertMessageTitle,
			i18n.tr.childData.alertMessageError,
			true,
		);
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
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				`${i18n.tr.childData.alertMessageUpdate} ${response.error.detail}`,
				true,
			);
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
			alertStore.showAlert(
				i18n.tr.childData.alertMessageTitle,
				`${i18n.tr.childData.alertMessageError} ${response.error.detail}`,
				true,
			);
			return;
		}
	} else {
		// DEBUG/TEMPORARY: this should never happen in the final version
		console.log("do nothing with image: ", imageDeleted, image, typeof image);
	}
}

async function submitData(): Promise<void> {
	console.log("Submit data called.");
	// submit child data
	await submitChildData();

	// handle image data
	await submitImageData();

	// disable all elements to make editing a conscious choice amd go back to childrenGallery
	console.log("submission of child data successful.");
	goto("/userLand/children/gallery");
}
</script>

{#if i18n.locale}
    <Breadcrumbs data={breadcrumbdata} />
    {#await promise}
        <div class = "flex justify-center items-center ">
            <Spinner /> <p>{i18n.tr.childData.loadingMessage}</p>
        </div>
    {:then { questionnaire, answers }}
            <div class="container m-2 mx-auto w-full pb-4">
                <Card class="container m-1 mx-auto w-full max-w-xl">
                    <Heading
                            tag="h3"
                            class="m-1 mb-1 p-1 text-left font-bold tracking-tight text-gray-700 dark:text-gray-400"
                    >{childLabel}
                        {#if disableEdit}
                             <DangerousDeleteModal bind:open={showDeleteModal}
                                    afterDelete={() => goto("/userLand/children/gallery")}
                                    intendedConfirmCode={i18n.tr.admin.delete}
                                    deleteDryRunnableRequest={(dryRun) =>
                                    deleteChild({
                                        path: {
                                            child_id: currentChild.id,
                                        },
                                        query: {
                                            dry_run: dryRun
                                        }
                                    })}>

                                </DangerousDeleteModal>
                            <small class="block text-muted">
                                <span class="text-muted">{birthmonthtext} {birthyear}</span>
                            </small>
                        {/if}
                    </Heading
                    >
                    <form
                            class="m-1 mx-auto w-full flex-col space-y-6"
                            onsubmit={preventDefault(submitData)}
                    >
                        {#if false === disableEdit && showChildQuestions === false}
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

                            {#if displayChildImages}
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


                                {#if image !== null && disableEdit === false}

                                    <div class="text-center" style="min-width:100%">
                                        <div>
                                            <img src={URL.createObjectURL(image)} alt="Child preview" style="width: 100%; max-height: 200px; object-fit: contain;" />
                                        </div>
                                        <div>
                                        <DeleteButton onclick={() => {
                                                image = null;
                                                disableImageDelete = true;
                                                imageDeleted = true;
                                        }} />
                                        </div>
                                    </div>
                                {:else if disableImageDelete === true}
                                    <p class="text-center text-sm text-gray-700 dark:text-gray-400 flex items-center justify-center">
                                        <CheckCircleOutline size="lg" color="green"/> {i18n.tr.childData.imageOfChildChangeDelete}
                                    </p>
                                {/if}
                            {/if}
                        {/if}


                        <span>
                            {#if disableEdit}
                                <EditButton onclick={() => disableEdit = false} />
                            {/if}

                            {#if currentChild.id !== null && disableEdit === true}
                                    <DeleteButton onclick={() => showDeleteModal = true} />
                                {/if}
                            {#if !showChildQuestions && disableEdit}
                                <Button class="btn-secondary btn-icon" style="padding: 9.5px 20px" on:click={() => {
                                    showChildQuestions = true;
                                    disableEdit = false;
                                }}>
                                      <ClipboardCheckOutline /> {questionnaire.length} {i18n.tr.admin.questions}

                                </Button>
                                <Tooltip>{questionnaire.length} {i18n.tr.admin.childQuestions}</Tooltip>
                            {/if}

                        </span>

                        <hr style="margin-bottom:10px" />

                        {#if currentChild.id !== null && disableEdit === true}
                            <Button
                                    class="btn-primary"
                                    onclick={() => {
                                        goto(`/userLand/children/feedback`)
                                    }}>
                                <ChartLineUpOutline size="md" />
                                {i18n.tr.childData.feedbackButtonLabel}
                            </Button>
                            <Button
                                    class="btn-primary"
                                    onclick={() => {
                                        goto(`/userLand/milestone/group`)
                                    }}
                            >
                                <FlagOutline size="md" />
                                {i18n.tr.childData.nextButtonLabel}
                            </Button>

                        {/if}

                        {#if (!disableEdit || (disableEdit && showChildQuestions))}
                            {#each questionnaire as element, i}
                                <DataInput
                                        component={element.component ? componentTable[element.component] : undefined}
                                        bind:value={answers[element.id].answer}
                                        bind:additionalValue={answers[element.id].additional_answer}
                                        label={element?.text?.[i18n.locale].question}
                                        textTrigger={element.additional_option}
                                        required={element.required}
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
                        {/if}
                        {#if disableEdit === false}
                            <button
                                    class="btn-primary"
                                    type="submit"
                            >{i18n.tr.childData.submitButtonLabel}</button
                            >
                        {/if}
                    </form>
                </Card>
            </div>
    {:catch error}
        {alertStore.showAlert(i18n.tr.childData.alertMessageTitle, error.message, true, true)}
    {/await}
{:else}
    {alertStore.showAlert(i18n.tr.childData.alertMessageTitle, i18n.tr.childData.alertMessageError, true)}
{/if}
