<svelte:options runes={true} />

<script lang="ts">
import {
	type AdminSettingsPublic,
	getAdminSettings,
	updateAdminSettings,
} from "$lib/client";
import { i18n } from "$lib/i18n.svelte";
import { Card, Toggle } from "flowbite-svelte";
import { CheckCircleOutline } from "flowbite-svelte-icons";
import { onMount } from "svelte";

// State for admin settings
let adminSettings: AdminSettingsPublic = $state({
	hide_milestone_feedback: false,
	hide_milestone_group_feedback: false,
	hide_all_feedback: false,
});

let loading: boolean = $state(true);
let error: string | null = $state(null);
let showSuccessMessage: boolean = $state(false);
let successTimeout: NodeJS.Timeout | null = $state(null);

// Load admin settings on component mount
onMount(async () => {
	await loadAdminSettings();
});

async function loadAdminSettings() {
	try {
		loading = true;
		error = null;

		const response = await getAdminSettings();
		if (!response.data) {
			throw new Error("No data received from API");
		}
		adminSettings = response.data;
	} catch (e) {
		error = e instanceof Error ? e.message : "Failed to load admin settings"; // catches the error above if data missing
	} finally {
		loading = false;
	}
}

async function updateSettings(
	field: keyof AdminSettingsPublic,
	value: boolean,
) {
	try {
		error = null;
		showSuccessMessage = false;

		const response = await updateAdminSettings({
			body: { [field]: value },
		});
		if (!response.data) {
			throw new Error("No data received from API");
		}
		const updatedSettings = response.data;
		adminSettings = updatedSettings;

		showSuccessMessage = true;

		if (successTimeout) {
			clearTimeout(successTimeout);
		}
		successTimeout = setTimeout(() => {
			showSuccessMessage = false;
		}, 3000);
	} catch (e) {
		error = e instanceof Error ? e.message : "Failed to update admin settings";
		adminSettings[field] = !value;
	}
}
</script>

<h3 class="mb-3 text-xl font-medium text-gray-900 dark:text-white">{i18n.tr.admin.feedbackConfiguration}</h3>

{#if loading}
    <p class="text-gray-500">Loading settings...</p>
{:else if error}
    <div class="mb-4 p-4 text-red-800 bg-red-100 rounded-lg dark:bg-red-900 dark:text-red-300">
        {error}
    </div>
{:else}
    <Card class="max-w-lg">
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <label for="hide-milestone-feedback" class="text-sm font-medium text-gray-900 dark:text-white">
                   {i18n.tr.admin.hideMilestoneFeedback}
                </label>
                <Toggle
                    id="hide-milestone-feedback"
                    checked={adminSettings.hide_all_feedback || adminSettings.hide_milestone_feedback}
                    disabled={adminSettings.hide_all_feedback}
                    on:change={(e) => updateSettings('hide_milestone_feedback', e.target.checked)}
                />
            </div>

            <div class="flex items-center justify-between">
                <label for="hide-milestone-group-feedback" class="text-sm font-medium text-gray-900 dark:text-white">
                    {i18n.tr.admin.hideMilestoneGroupFeedback}
                </label>
                <Toggle
                    id="hide-milestone-group-feedback"
                    checked={adminSettings.hide_all_feedback || adminSettings.hide_milestone_group_feedback}
                    disabled={adminSettings.hide_all_feedback}
                    on:change={(e) => updateSettings('hide_milestone_group_feedback', e.target.checked)}
                />
            </div>

            <div class="flex items-center justify-between">
                <label for="hide-all-feedback" class="text-sm font-medium text-gray-900 dark:text-white">
                    {i18n.tr.admin.hideAllFeedback}
                </label>
                <Toggle
                    id="hide-all-feedback"
                    bind:checked={adminSettings.hide_all_feedback}
                    on:change={(e) => updateSettings('hide_all_feedback', e.target.checked)}
                />
            </div>
        </div>

        {#if showSuccessMessage}
            <div class="mt-4 p-3 text-green-800 bg-green-100 rounded-lg border border-green-200 dark:bg-green-900 dark:text-green-300 dark:border-green-800">
                <div class="flex items-center">
                    <CheckCircleOutline class="w-4 h-4 mr-2" />
                    <span class="text-sm font-medium">{i18n.tr.admin.feedbackConfigurationNote}</span>
                </div>
            </div>
        {/if}
    </Card>
{/if}
