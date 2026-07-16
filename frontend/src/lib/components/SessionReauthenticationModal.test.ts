import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.hoisted(() => {
	window.matchMedia = vi.fn().mockReturnValue({
		addEventListener: vi.fn(),
		matches: false,
		removeEventListener: vi.fn(),
	});
});

const mocks = vi.hoisted(() => ({
	reauthenticateSession: vi.fn(),
}));

vi.mock("$lib/client/sdk.gen", () => ({
	reauthenticateSession: mocks.reauthenticateSession,
}));
vi.mock("$lib/i18n.svelte", () => ({
	i18n: {
		tr: {
			login: {
				incorrectPassword: "Incorrect password",
				passwordLabel: "Password",
				reauthenticate: "Extend session",
				reauthenticationError: "Unable to extend session",
				sessionAbsoluteExpiringMessage: "Enter your password",
				sessionExpiringMessage: "Continue?",
				sessionExpiringTitle: "Session expiring",
				staySignedIn: "Stay signed in",
			},
		},
	},
}));

import SessionReauthenticationModal from "$lib/components/SessionReauthenticationModal.svelte";
import { sessionStore } from "$lib/stores/sessionStore.svelte";

function renewedSessionResponse() {
	return new Response(null, {
		status: 204,
		headers: {
			"X-Session-Absolute-Expires-At": new Date(
				Date.now() + 8 * 60 * 60 * 1000,
			).toISOString(),
			"X-Session-Idle-Expires-At": new Date(
				Date.now() + 60 * 60 * 1000,
			).toISOString(),
			"X-Session-Warning-Seconds": "300",
		},
	});
}

describe("session reauthentication modal", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		sessionStore.clear();
		sessionStore.isReauthenticationShown = true;
	});

	it("reauthenticates without navigating away", async () => {
		mocks.reauthenticateSession.mockResolvedValue({
			data: undefined,
			error: undefined,
			response: renewedSessionResponse(),
		});
		render(SessionReauthenticationModal);

		await fireEvent.input(screen.getByLabelText("Password"), {
			target: { value: "secret" },
		});
		await fireEvent.click(
			screen.getByRole("button", { name: "Extend session" }),
		);

		await waitFor(() => {
			expect(mocks.reauthenticateSession).toHaveBeenCalledWith({
				body: { password: "secret" },
			});
			expect(sessionStore.isReauthenticationShown).toBe(false);
		});
	});

	it("keeps the modal open after an incorrect password", async () => {
		mocks.reauthenticateSession.mockResolvedValue({
			data: undefined,
			error: {},
			response: new Response(null, { status: 400 }),
		});
		render(SessionReauthenticationModal);

		await fireEvent.input(screen.getByLabelText("Password"), {
			target: { value: "wrong" },
		});
		await fireEvent.click(
			screen.getByRole("button", { name: "Extend session" }),
		);

		expect((await screen.findByRole("alert")).textContent).toContain(
			"Incorrect password",
		);
		expect(sessionStore.isReauthenticationShown).toBe(true);
	});
});
