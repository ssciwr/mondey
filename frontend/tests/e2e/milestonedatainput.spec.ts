import { test } from "@playwright/test";
import { login } from "./utils";

test("/userLand/children/gallery - Can add Child", async ({
	page,
	isMobile,
}) => {
	await login(page, "admin@mondey.de", "admin"); // todo: Login as parent.
	await page.getByText("Kinder").click();
	// choose specific child.
	// we make another one here so that the existing one with milestone data for this parent does not get affected
	// on the feedback page for the feedback test.
	// click on the childs name on Kinder page.
	// click on the button with the text "Weiter zu Meilensteinen"
	// click on the h5 with the text "Reading skills" (this will bea  milestoen group)
	// click on the h5 with the text "Recognizes Digits"
	// assert the page contains "Recognizes Digits"  and ... description·
	// CLick on the button with the text "Weitgehend"
});
