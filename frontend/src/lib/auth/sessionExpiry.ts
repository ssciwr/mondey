import { goto } from "$app/navigation";
import type { RequestOptions } from "$lib/client/client";

import { client } from "$lib/client/client.gen";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { sessionStore } from "$lib/stores/sessionStore.svelte";
import { user } from "$lib/stores/userStore.svelte";

function expireSession(redirectImmediately: boolean) {
	if (!user.data) {
		return;
	}

	const intendedPath = `${window.location.pathname}${window.location.search}`;
	const searchParams = new URLSearchParams({ intendedpath: intendedPath });
	const redirectToLogin = () => {
		void goto(`/login?${searchParams.toString()}`);
	};

	// Clear the cached user immediately. This also prevents concurrent failed
	// requests from handling the same expiry more than once.
	sessionStore.clear();
	user.data = null;

	if (redirectImmediately) {
		alertStore.hideAlert();
		redirectToLogin();
		return;
	}

	alertStore.showAlert(
		i18n.tr.login.sessionExpiredTitle,
		i18n.tr.login.sessionExpiredMessage,
		true,
		false,
		redirectToLogin,
		null,
		{ priority: 1 },
	);
}

function handleSessionExpiry(
	response: Response,
	_request: Request,
	options: RequestOptions,
): Response {
	if (!options.security) {
		return response;
	}
	if (response.status !== 401) {
		sessionStore.updateFromResponse(response);
		return response;
	}
	if (!user.data) {
		return response;
	}

	expireSession(false);

	return response;
}

export function installSessionExpiryHandler(): () => void {
	client.interceptors.response.use(handleSessionExpiry);
	const removeExpirationHandler = sessionStore.onExpiration(() => {
		expireSession(true);
	});
	return () => {
		client.interceptors.response.eject(handleSessionExpiry);
		removeExpirationHandler();
	};
}
