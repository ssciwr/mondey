<svelte:options runes={true} />

<script lang="ts">
import CancelButton from "$lib/components/Admin/CancelButton.svelte";
import InputAutoTranslate from "$lib/components/Admin/InputAutoTranslate.svelte";
import SaveButton from "$lib/components/Admin/SaveButton.svelte";
import { i18n } from "$lib/i18n.svelte";
import type { Translation } from "$lib/i18n.svelte";
import { Label, Modal } from "flowbite-svelte";

let {
	open = $bindable(false),
	translations = $bindable({}),
	missing_translations,
	onsave,
}: {
	open: boolean;
	translations: Record<string, Translation>;
	missing_translations: Array<string>;
	onsave: () => Promise<void>;
} = $props();

let idx = $state(0);
let successMessage = $state(null as string | null);
</script>

<Modal title={i18n.tr.admin.missingTranslations} bind:open outsideclose size="lg">
    {#if successMessage}
        <div class="mb-4 px-4 py-2 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            {successMessage}
        </div>
    {/if}

    {#if missing_translations.length > 0}
        {@const section_key = missing_translations[idx].split(".")[0]}
        {@const item_key = missing_translations[idx].split(".")[1]}
            <Label class="mb-2">{missing_translations[idx]}</Label>
            {#each i18n.locales as lang}
                <div class="mb-1">
                    <InputAutoTranslate bind:value={translations[lang][section_key][item_key]} locale={lang} de_text={translations["de"][section_key][item_key]}/>
                </div>
            {/each}
    {/if}
    <svelte:fragment slot="footer">
        <SaveButton onclick={async () => {
            await onsave(); 
            successMessage = i18n.tr.admin.saveChanges + " ✓";
            setTimeout(() => {
                successMessage = null;
                if(idx+1<missing_translations.length) {
                    ++idx;
                } else {
                    open = false;
                }
            }, 2000);
        }}/>
        <CancelButton onclick={() => {open = false;}}/>
    </svelte:fragment>
</Modal>
