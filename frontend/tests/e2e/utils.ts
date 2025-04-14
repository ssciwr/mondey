import type { Page } from "@playwright/test";

export async function login(page: Page, username: string, password: string) {
	await page.goto("/login", { waitUntil: "networkidle" });
	await page.fill("#username", username);
	await page.fill("#password", password);
	await page.getByRole("button", { name: "Absenden" }).click();
}

// Would be good to improve this.
export const modalLoad = async (page: Page) => page.waitForTimeout(5000);
