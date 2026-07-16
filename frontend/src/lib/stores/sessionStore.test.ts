import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
	handleExpiration: vi.fn(),
	showAlert: vi.fn(),
	usersCurrentUser: vi.fn(),
}));

vi.mock("$lib/client/sdk.gen", () => ({
	usersCurrentUser: mocks.usersCurrentUser,
}));
vi.mock("$lib/i18n.svelte", () => ({
	i18n: {
		tr: {
			login: {
				sessionAbsoluteExpiringMessage: "Sign in again",
				sessionExpiringMessage: "Continue?",
				sessionExpiringTitle: "Session expiring",
				staySignedIn: "Stay signed in",
			},
		},
	},
}));
vi.mock("$lib/stores/alertStore.svelte", () => ({
	alertStore: { showAlert: mocks.showAlert },
}));

import { sessionStore } from "$lib/stores/sessionStore.svelte";

function sessionResponse(
	idleMilliseconds: number,
	absoluteMilliseconds: number,
) {
	return new Response(null, {
		headers: {
			"X-Session-Absolute-Expires-At": new Date(
				Date.now() + absoluteMilliseconds,
			).toISOString(),
			"X-Session-Idle-Expires-At": new Date(
				Date.now() + idleMilliseconds,
			).toISOString(),
			"X-Session-Warning-Seconds": "10",
		},
	});
}

describe("session warning store", () => {
	let removeExpirationHandler: () => void;

	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2026-07-15T12:00:00Z"));
		vi.clearAllMocks();
		mocks.usersCurrentUser.mockResolvedValue({ data: {}, error: undefined });
		sessionStore.clear();
		removeExpirationHandler = sessionStore.onExpiration(mocks.handleExpiration);
	});

	afterEach(() => {
		sessionStore.clear();
		removeExpirationHandler();
		vi.useRealTimers();
	});

	it("warns before idle expiry and refreshes on confirmation", async () => {
		sessionStore.updateFromResponse(sessionResponse(60_000, 600_000));

		vi.advanceTimersByTime(49_999);
		expect(mocks.showAlert).not.toHaveBeenCalled();
		vi.advanceTimersByTime(1);
		expect(mocks.showAlert).toHaveBeenCalledWith(
			"Session expiring",
			"Continue?",
			false,
			false,
			expect.any(Function),
			"Stay signed in",
		);
		expect(vi.getTimerCount()).toBe(1);

		const staySignedIn = mocks.showAlert.mock.calls[0][4] as () => void;
		staySignedIn();
		await vi.waitFor(() =>
			expect(mocks.usersCurrentUser).toHaveBeenCalledOnce(),
		);
	});

	it("reuses one timer for the warning and exact expiry", () => {
		sessionStore.updateFromResponse(sessionResponse(60_000, 600_000));
		expect(vi.getTimerCount()).toBe(1);

		vi.advanceTimersByTime(50_000);
		expect(mocks.showAlert).toHaveBeenCalledOnce();
		expect(vi.getTimerCount()).toBe(1);

		vi.advanceTimersByTime(9_999);
		expect(mocks.handleExpiration).not.toHaveBeenCalled();
		vi.advanceTimersByTime(1);
		expect(mocks.handleExpiration).toHaveBeenCalledOnce();
		expect(vi.getTimerCount()).toBe(0);
	});

	it("requests reauthentication when the absolute timeout comes first", () => {
		sessionStore.updateFromResponse(sessionResponse(600_000, 60_000));

		vi.advanceTimersByTime(50_000);

		expect(sessionStore.isReauthenticationShown).toBe(true);
		expect(mocks.showAlert).not.toHaveBeenCalled();
		expect(vi.getTimerCount()).toBe(1);

		// A rotated session has a later absolute expiry and closes the prompt.
		sessionStore.updateFromResponse(sessionResponse(600_000, 600_000));
		expect(sessionStore.isReauthenticationShown).toBe(false);
		expect(vi.getTimerCount()).toBe(1);
	});
});
