import { type Page, expect, test } from "@playwright/test";
import type {
	MilestoneAdmin,
	MilestoneGroupAdmin,
} from "../../src/lib/client/types.gen";
import { login } from "./utils";

async function createMilestoneGroup(page: Page, title: string) {
	const createResponse = await page.request.post(
		"/api/admin/milestone-groups/",
	);
	expect(createResponse.ok()).toBeTruthy();
	const group = (await createResponse.json()) as MilestoneGroupAdmin;
	for (const text of Object.values(group.text)) {
		text.title = title;
	}

	const updateResponse = await page.request.put("/api/admin/milestone-groups", {
		data: group,
	});
	expect(updateResponse.ok()).toBeTruthy();
	return group;
}

async function createMilestone(page: Page, groupId: number, title: string) {
	const createResponse = await page.request.post(
		`/api/admin/milestones/${groupId}`,
	);
	expect(createResponse.ok()).toBeTruthy();
	const milestone = (await createResponse.json()) as MilestoneAdmin;
	milestone.name = title;
	for (const text of Object.values(milestone.text)) {
		text.title = title;
	}

	const updateResponse = await page.request.put("/api/admin/milestones/", {
		data: milestone,
	});
	expect(updateResponse.ok()).toBeTruthy();
	return milestone;
}

test("admin can move a milestone to another group and recalculate statistics", async ({
	page,
}) => {
	await login(page, "admin@mondey.de", "admin");

	// Wait for login to finish, then create data owned by this test so browser projects can
	// run concurrently without moving the same milestone.
	await expect(page.locator('h5:has-text("+ Neu")')).toBeVisible();
	const suffix = crypto.randomUUID();
	const sourceTitle = `move-source-${suffix}`;
	const destinationTitle = `move-destination-${suffix}`;
	const milestoneTitle = `move-milestone-${suffix}`;
	const sourceGroup = await createMilestoneGroup(page, sourceTitle);
	await createMilestoneGroup(page, destinationTitle);
	const milestone = await createMilestone(page, sourceGroup.id, milestoneTitle);

	// Go to the admin page (the milestones tab is open by default).
	await page.getByText("Administration").click();
	await expect(page.getByText("Voraussichtliches Alter")).toBeVisible();

	// Expand the source group and open the milestone's edit modal.
	await page.getByText(sourceTitle, { exact: true }).click();
	const editMilestone = page.getByTestId(`edit-milestone-${milestone.id}`);
	await editMilestone.click();

	// change the milestone's group to the other group and save
	const groupSelect = page.getByTestId("milestoneGroupSelect");
	await expect(groupSelect).toBeVisible();
	await groupSelect.selectOption({ label: destinationTitle });
	await page.getByTestId("cancelButton").click();

	// Canceling must not mutate the milestone object held by the shared admin store.
	await editMilestone.click();
	await expect(groupSelect).toHaveValue(String(sourceGroup.id));
	await groupSelect.selectOption({ label: destinationTitle });
	await page.getByRole("button", { name: "Änderungen speichern" }).click();

	// the recalculation prompt is offered because the group changed
	await expect(page.getByText("Statistiken aktualisieren")).toBeVisible();
	await page.route("**/api/admin/update-stats/", async (route) => {
		await new Promise((resolve) => setTimeout(resolve, 250));
		await route.continue();
	});
	await page.getByTestId("recalculateStatsButton").click();
	await page.keyboard.press("Escape");
	await expect(page.getByRole("dialog")).toBeVisible();

	// wait for the recalculation to finish, then close the modal
	const closeButton = page.getByTestId("closeUpdateStatsModal");
	await expect(closeButton).toBeEnabled();
	await expect(page.getByText(/\d+ Antworten/)).toBeVisible();
	await closeButton.click();
	await expect(closeButton).toBeHidden();

	// the milestone now appears under the destination group
	await page.getByText(destinationTitle, { exact: true }).click();
	await expect(page.getByText(milestoneTitle, { exact: true })).toBeVisible();
});
