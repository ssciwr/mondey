<svelte:options runes={true} />
<script lang="ts">
import { type AgeInterval, getAgeIntervals } from "$lib/client";
import AddButton from "$lib/components/Admin/AddButton.svelte";
import { Hr, Spinner } from "flowbite-svelte";
import { _ } from "svelte-i18n";
import AlertMessage from "../AlertMessage.svelte";
import EditAgeIntervalModal from "./EditAgeIntervalModal.svelte";
import EditButton from "./EditButton.svelte";

let alertMessage = $state($_("userData.alertMessageError"));
let showAlert = $state(false);
let openEdit = $state(false);
let ageintervals: AgeInterval[] = $state([]);

async function setup(): Promise<AgeInterval[]> {
	const ageintervalsResponse = await getAgeIntervals();

	if (ageintervalsResponse.error) {
		showAlert = true;
		alertMessage = `${$_("userData.alertMessageError")} {ageintervals.error.detail}`;
		return [] as AgeInterval[];
	}
	ageintervals = ageintervalsResponse.data as AgeInterval[];
	return ageintervals;
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

    {#each data as ageinterval, idx}
        <div>
            <p>{ageinterval.id}</p>
            <p>{ageinterval.lower_limit}</p>
            <p>{ageinterval.upper_limit}</p>
			<EditButton onclick={() => {openEdit = true;}} />
			<EditAgeIntervalModal bind:show={openEdit} bind:interval={data[idx]} />
        </div>
    {/each}

    <Hr classHr="mx-2" />

    <AddButton onclick = {()=>{
            openEdit = true;
            }}/>
    <EditAgeIntervalModal bind:show={openEdit}/>

{:catch error}
	<AlertMessage
		title={"Error in server request"}
		message={error.message}
		onclick={() => {
			showAlert = false;
		}}
	/>
{/await}
