import {expect, test} from "@playwright/test";

/*
// Just mocking how we could do this, if we have the backend running in a playwright context.
test(`/ : Anonymous users can log in`, async ({ page }) => {
    await page.goto(`/`);
    const button = page.getByText("Try Demo");
    await button.click()
    await expect(page).toHaveURL('/userLand/userLandingpage');
    await expect(page.getByText("Kinder")).toBeVisible();
    // todo; This test requires mocking, or actual running backend, anyhow.
    const isLoggedIn = await page.evaluate(async () => {
        const { user } = await import('$lib/stores/userStore.svelte');
        if (user.data === null) {
            await user.load();
        }
        return user.data !== null;
    });
    expect(isLoggedIn).toBeTruthy();
});

 */