import { expect, test } from "@playwright/test";
import { login, modalLoad } from "./utils";

test("/userLand/children/gallery - Can add Child", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin");
	await page.getByText("Kinder").click();
	await page.locator('h5:has-text("+ Neu")').click();
	await modalLoad(page);
	const element_when_adding = page.getByText("Name des Kindes?");
	await expect(element_when_adding).toBeTruthy();
	/*
    # first bit = the "for" values for these <inputs> to find them. After "-->", the value to type in.
    Names des Kindes? --> type "TestChild"
    Geburtsmonat des Kindes? --> type "3"
    Geburtsjahr des Kindes? --> type "2025"

    # then click the button with text : Abschließen

    */
});
