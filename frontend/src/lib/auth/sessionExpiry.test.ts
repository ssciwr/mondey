import type { RequestOptions } from "$lib/client/client";
import { beforeEach, describe, expect, it, vi } from "vitest";

type ResponseHandler = (
	response: Response,
	request: Request,
	options: RequestOptions,
) => Response;

const mocks = vi.hoisted(() => ({
	eject: vi.fn(),
	goto: vi.fn(),
	hideAlert: vi.fn(),
	onExpiration: vi.fn(),
	removeExpirationHandler: vi.fn(),
	responseUse: vi.fn(),
	sessionClear: vi.fn(),
	sessionUpdate: vi.fn(),
	showAlert: vi.fn(),
	user: { data: { id: 1 } as { id: number } | null },
}));

vi.mock("$app/navigation", () => ({ goto: mocks.goto }));
vi.mock("$lib/client/client.gen", () => ({
	client: {
		interceptors: {
			response: { eject: mocks.eject, use: mocks.responseUse },
		},
	},
}));
vi.mock("$lib/i18n.svelte", () => ({
	i18n: {
		tr: {
			login: {
				sessionExpiredMessage: "Changes were not saved",
				sessionExpiredTitle: "Session expired",
			},
		},
	},
}));
vi.mock("$lib/stores/alertStore.svelte", () => ({
	alertStore: { hideAlert: mocks.hideAlert, showAlert: mocks.showAlert },
}));
vi.mock("$lib/stores/sessionStore.svelte", () => ({
	sessionStore: {
		clear: mocks.sessionClear,
		onExpiration: mocks.onExpiration,
		updateFromResponse: mocks.sessionUpdate,
	},
}));
vi.mock("$lib/stores/userStore.svelte", () => ({ user: mocks.user }));

import { installSessionExpiryHandler } from "$lib/auth/sessionExpiry";

function installAndGetHandler(): ResponseHandler {
	installSessionExpiryHandler();
	return mocks.responseUse.mock.calls[0][0] as ResponseHandler;
}

describe("session expiry response handler", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.onExpiration.mockReturnValue(mocks.removeExpirationHandler);
		mocks.user.data = { id: 1 };
		window.history.replaceState({}, "", "/userLand/admin?section=milestones");
	});

	it("clears the user, warns once, and redirects back through login", () => {
		const handler = installAndGetHandler();
		const response = new Response(null, { status: 401 });

		expect(
			handler(response, new Request("https://example.com/api/admin"), {
				security: [{ in: "cookie", name: "fastapiusersauth", type: "apiKey" }],
				url: "/api/admin",
			}),
		).toBe(response);
		expect(mocks.user.data).toBeNull();
		expect(mocks.sessionClear).toHaveBeenCalledOnce();
		expect(mocks.showAlert).toHaveBeenCalledOnce();
		expect(mocks.showAlert).toHaveBeenCalledWith(
			"Session expired",
			"Changes were not saved",
			true,
			false,
			expect.any(Function),
			null,
			{ priority: 1 },
		);

		const acknowledge = mocks.showAlert.mock.calls[0][4] as () => void;
		acknowledge();
		expect(mocks.goto).toHaveBeenCalledWith(
			"/login?intendedpath=%2FuserLand%2Fadmin%3Fsection%3Dmilestones",
		);

		// A concurrent 401 is ignored after the first one cleared the user.
		handler(response, new Request("https://example.com/api/admin"), {
			security: [{ in: "cookie", name: "fastapiusersauth", type: "apiKey" }],
			url: "/api/admin",
		});
		expect(mocks.showAlert).toHaveBeenCalledOnce();
	});

	it("updates session timing from authenticated responses", () => {
		const handler = installAndGetHandler();
		const response = new Response(null, { status: 200 });

		handler(response, new Request("https://example.com/api/admin"), {
			security: [{ in: "cookie", name: "fastapiusersauth", type: "apiKey" }],
			url: "/api/admin",
		});

		expect(mocks.sessionUpdate).toHaveBeenCalledWith(response);
		expect(mocks.showAlert).not.toHaveBeenCalled();
	});

	it("redirects immediately when the client-side expiry timer fires", () => {
		installAndGetHandler();
		const expire = mocks.onExpiration.mock.calls[0][0] as () => void;

		expire();

		expect(mocks.sessionClear).toHaveBeenCalledOnce();
		expect(mocks.user.data).toBeNull();
		expect(mocks.hideAlert).toHaveBeenCalledOnce();
		expect(mocks.showAlert).not.toHaveBeenCalled();
		expect(mocks.goto).toHaveBeenCalledWith(
			"/login?intendedpath=%2FuserLand%2Fadmin%3Fsection%3Dmilestones",
		);
	});

	it("does not treat an unauthenticated request as an expired session", () => {
		const handler = installAndGetHandler();

		handler(
			new Response(null, { status: 401 }),
			new Request("https://example.com/api/auth/login"),
			{ url: "/api/auth/login" },
		);

		expect(mocks.user.data).toEqual({ id: 1 });
		expect(mocks.showAlert).not.toHaveBeenCalled();
	});

	it("removes the interceptor during layout cleanup", () => {
		const uninstall = installSessionExpiryHandler();
		const handler = mocks.responseUse.mock.calls[0][0];

		uninstall();

		expect(mocks.eject).toHaveBeenCalledWith(handler);
		expect(mocks.removeExpirationHandler).toHaveBeenCalledOnce();
	});
});
