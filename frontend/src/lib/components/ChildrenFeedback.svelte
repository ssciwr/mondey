<svelte:options runes={true} />
<script lang="ts">
import {
	type MilestoneAnswerSessionPublic,
	getExpiredMilestoneAnswerSessions,
} from "$lib/client";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { Spinner } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "./AlertMessage.svelte";

async function setup(): Promise<void> {
	user.load;
	await currentChild.load_data();

	if (currentChild.id === null || user.id === null) {
		showAlert = true;
		return;
	}

	let response = await getExpiredMilestoneAnswerSessions({
		path: { child_id: currentChild.id as number },
	});
	console.log("response: ", response);
	if (response.error) {
		showAlert = true;
		return;
	}
	answerSessions = response.data;
}

let promise = setup();
let showAlert = $state(false);
let answerSessions = $state([] as MilestoneAnswerSessionPublic[]);

$effect(() => {
	console.log(answerSessions);
});
</script>

{#await promise}
<Spinner /> {$_("childData.loadingMessage")}
{:then _}
<div>
    TODO: implement childrenfeedback visuals
</div>
{:catch error}
<AlertMessage
    message = {$_("childData.alertMessageError")}
    title = {$_("childData.alertMessageTitle")}


/>
{/await}
