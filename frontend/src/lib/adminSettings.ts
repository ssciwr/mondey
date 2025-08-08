/**
 * Utility functions for managing admin settings
 */

export interface AdminSettings {
	hide_milestone_feedback: boolean;
	hide_milestone_group_feedback: boolean;
	hide_all_feedback: boolean;
}

export interface AdminSettingsUpdate {
	hide_milestone_feedback?: boolean;
	hide_milestone_group_feedback?: boolean;
	hide_all_feedback?: boolean;
}

/**
 * Fetches the current admin settings from the API
 * @returns Promise resolving to admin settings data
 * @throws Error if the request fails
 */
export async function getAdminSettings(): Promise<AdminSettings> {
	const response = await fetch("/api/admin/settings/", {
		method: "GET",
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
	});

	if (!response.ok) {
		throw new Error(
			`Failed to fetch admin settings: ${response.status} ${response.statusText}`,
		);
	}

	return response.json();
}

/**
 * Updates admin settings with partial data
 * @param updates - Partial admin settings object with fields to update
 * @returns Promise resolving to updated admin settings data
 * @throws Error if the request fails
 */
export async function updateAdminSettings(
	updates: AdminSettingsUpdate,
): Promise<AdminSettings> {
	const response = await fetch("/api/admin/settings/", {
		method: "PUT",
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(updates),
	});

	if (!response.ok) {
		throw new Error(
			`Failed to update admin settings: ${response.status} ${response.statusText}`,
		);
	}

	return response.json();
}
