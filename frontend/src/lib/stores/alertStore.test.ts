import { beforeEach, describe, expect, it } from "vitest";

import { alertStore } from "$lib/stores/alertStore.svelte";

describe("alert store priority", () => {
	beforeEach(() => alertStore.hideAlert());

	it("does not replace a higher-priority alert", () => {
		alertStore.showAlert(
			"Session expired",
			"Please sign in again",
			true,
			false,
			null,
			null,
			{ priority: 1 },
		);

		alertStore.showAlert("Error", "Please try again", true, true);

		expect(alertStore.title).toBe("Session expired");
		expect(alertStore.message).toBe("Please sign in again");
	});

	it("allows a higher-priority alert to replace a normal alert", () => {
		alertStore.showAlert("Error", "Please try again", true, true);

		alertStore.showAlert(
			"Session expired",
			"Please sign in again",
			true,
			false,
			null,
			null,
			{ priority: 1 },
		);

		expect(alertStore.title).toBe("Session expired");
	});
});
