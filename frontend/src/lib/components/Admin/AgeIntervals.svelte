<svelte:options runes={true} />
<script lang="ts">
import { type AgeInterval, getAgeIntervals } from "$lib/client";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import { Hr, Spinner } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "../AlertMessage.svelte";
import CreateAgeIntervalsModal from "./CreateAgeIntervalModal.svelte";

let alertMessage = $state($_("userData.alertMessageError"));
let showAlert = $state(false);
let showCreate = $state(false);

async function setup(): Promise<AgeInterval[]> {
	const ageintervals = await getAgeIntervals();

	if (ageintervals.error) {
		showAlert = true;
		alertMessage = `${$_("userData.alertMessageError")} {ageintervals.error.detail}`;
		return [] as AgeInterval[];
	}
	return ageintervals.data;
}

let promise = setup();
</script>

{#await promise}
	<Spinner /> <p>{$_("userData.loadingMessage")}</p>
{:then data}
	{#if showAlert}
		<AlertMessage
			title={$_("childData.alertMessageTitle")}
			message={alertMessage}
			onclick={() => {
				showAlert = false;
			}}
		/>
	{/if}

    {#each data as ageinterval}
        <div>
            <p>{ageinterval.id}</p>
            <p>{ageinterval.lower_limit}</p>
            <p>{ageinterval.upper_limit}</p>
        </div>
    {/each}
    <Hr classHr="mx-2" />

    <AddButton onclick = {()=>{
            showCreate = true;
            }}/>

    <CreateAgeIntervalsModal bind:show={showCreate} />

{:catch error}
	<AlertMessage
		title={"Error in server request"}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
