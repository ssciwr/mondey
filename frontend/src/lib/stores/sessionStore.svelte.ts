import { usersCurrentUser } from "$lib/client/sdk.gen";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";

const idleExpiresHeader = "X-Session-Idle-Expires-At";
const absoluteExpiresHeader = "X-Session-Absolute-Expires-At";
const warningSecondsHeader = "X-Session-Warning-Seconds";

function createSessionStore() {
	let idleExpiresAt: number | null = null;
	let absoluteExpiresAt: number | null = null;
	let warningSeconds = 300;
	let sessionTimeout: ReturnType<typeof setTimeout> | null = null;
	let expirationHandler: (() => void) | null = null;
	let absoluteWarningShown = false;
	let reauthenticationShown = $state(false);

	function clearTimer() {
		if (sessionTimeout !== null) {
			clearTimeout(sessionTimeout);
			sessionTimeout = null;
		}
	}

	function clear() {
		clearTimer();
		idleExpiresAt = null;
		absoluteExpiresAt = null;
		absoluteWarningShown = false;
		reauthenticationShown = false;
	}

	async function staySignedIn() {
		const { error } = await usersCurrentUser();
		if (error) {
			console.log("Unable to refresh session", error);
		}
	}

	function expiresAt() {
		if (idleExpiresAt === null || absoluteExpiresAt === null) {
			return null;
		}
		return Math.min(idleExpiresAt, absoluteExpiresAt);
	}

	function scheduleExpiration() {
		clearTimer();
		const expiry = expiresAt();
		if (expiry === null) {
			return;
		}
		sessionTimeout = setTimeout(
			() => {
				sessionTimeout = null;
				expirationHandler?.();
			},
			Math.max(0, expiry - Date.now()),
		);
	}

	function showWarning() {
		if (idleExpiresAt === null || absoluteExpiresAt === null) {
			return;
		}
		// Reuse the same timer for exact expiry after it has fired for the warning.
		scheduleExpiration();
		if (absoluteExpiresAt <= idleExpiresAt) {
			if (absoluteWarningShown) {
				return;
			}
			absoluteWarningShown = true;
			reauthenticationShown = true;
			return;
		}
		alertStore.showAlert(
			i18n.tr.login.sessionExpiringTitle,
			i18n.tr.login.sessionExpiringMessage,
			false,
			false,
			() => {
				void staySignedIn();
			},
			i18n.tr.login.staySignedIn,
		);
	}

	function scheduleWarning() {
		clearTimer();
		const expiry = expiresAt();
		if (expiry === null) {
			return;
		}
		if (expiry <= Date.now()) {
			scheduleExpiration();
			return;
		}
		const delay = Math.max(0, expiry - Date.now() - warningSeconds * 1000);
		sessionTimeout = setTimeout(showWarning, delay);
	}

	function onExpiration(handler: () => void) {
		expirationHandler = handler;
		return () => {
			if (expirationHandler === handler) {
				expirationHandler = null;
			}
		};
	}

	function updateFromResponse(response: Response) {
		const idleValue = response.headers.get(idleExpiresHeader);
		const absoluteValue = response.headers.get(absoluteExpiresHeader);
		const warningValue = response.headers.get(warningSecondsHeader);
		if (!idleValue || !absoluteValue || !warningValue) {
			return;
		}
		const parsedIdle = Date.parse(idleValue);
		const parsedAbsolute = Date.parse(absoluteValue);
		const parsedWarning = Number.parseInt(warningValue, 10);
		if (
			Number.isNaN(parsedIdle) ||
			Number.isNaN(parsedAbsolute) ||
			Number.isNaN(parsedWarning)
		) {
			return;
		}
		if (absoluteExpiresAt === null || parsedAbsolute > absoluteExpiresAt) {
			absoluteWarningShown = false;
			reauthenticationShown = false;
		}
		idleExpiresAt = parsedIdle;
		absoluteExpiresAt = parsedAbsolute;
		warningSeconds = parsedWarning;
		scheduleWarning();
	}

	return {
		clear,
		get isReauthenticationShown() {
			return reauthenticationShown;
		},
		set isReauthenticationShown(value: boolean) {
			reauthenticationShown = value;
		},
		onExpiration,
		updateFromResponse,
	};
}

export const sessionStore = createSessionStore();
