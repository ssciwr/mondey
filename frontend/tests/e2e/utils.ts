import type { Page } from "@playwright/test";

export async function login(page: Page, username: string, password: string) {
	await page.goto("/login", { waitUntil: "networkidle" });
	await page.fill("#username", username);
	await page.fill("#password", password);
	await page.getByRole("button", { name: "Absenden" }).click();
}
