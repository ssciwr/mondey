<svelte:options runes={true} />

<script lang="ts">
import {
	type AdminSettings,
	getAdminSettings,
	updateAdminSettings,
} from "$lib/adminSettings";
import { i18n } from "$lib/i18n.svelte";
import { Card, Toggle } from "flowbite-svelte";
import { onMount } from "svelte";

// State for admin settings
let adminSettings: AdminSettings = $state({
	hide_milestone_feedback: false,
	hide_milestone_group_feedback: false,
	hide_all_feedback: false,
});

let loading: boolean = $state(true);
let error: string | null = $state(null);

// Load admin settings on component mount
onMount(async () => {
	await loadAdminSettings();
});

async function loadAdminSettings() {
	try {
		loading = true;
		error = null;

		adminSettings = await getAdminSettings();
	} catch (e) {
		error = e instanceof Error ? e.message : "Failed to load admin settings";
		console.error("Error loading admin settings:", e);
	} finally {
		loading = false;
	}
}

async function updateSettings(field: keyof AdminSettings, value: boolean) {
	try {
		error = null;

		const updatedSettings = await updateAdminSettings({
			[field]: value,
		});
		adminSettings = updatedSettings;
	} catch (e) {
		error = e instanceof Error ? e.message : "Failed to update admin settings";
		console.error("Error updating admin settings:", e);
		// Revert the change on error
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
                    Hide milestone feedback (individual milestones)
                </label>
                <Toggle
                    id="hide-milestone-feedback"
                    bind:checked={adminSettings.hide_milestone_feedback}
                    on:change={(e) => updateSettings('hide_milestone_feedback', e.target.checked)}
                />
            </div>

            <div class="flex items-center justify-between">
                <label for="hide-milestone-group-feedback" class="text-sm font-medium text-gray-900 dark:text-white">
                    Hide milestone group feedback (Bereiche)
                </label>
                <Toggle
                    id="hide-milestone-group-feedback"
                    bind:checked={adminSettings.hide_milestone_group_feedback}
                    on:change={(e) => updateSettings('hide_milestone_group_feedback', e.target.checked)}
                />
            </div>

            <div class="flex items-center justify-between">
                <label for="hide-all-feedback" class="text-sm font-medium text-gray-900 dark:text-white">
                    Hide all feedback (completely disable feedback system)
                </label>
                <Toggle
                    id="hide-all-feedback"
                    bind:checked={adminSettings.hide_all_feedback}
                    on:change={(e) => updateSettings('hide_all_feedback', e.target.checked)}
                />
            </div>
        </div>
    </Card>
{/if}
