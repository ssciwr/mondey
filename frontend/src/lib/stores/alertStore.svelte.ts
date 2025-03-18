type AlertCallback = () => void;

/**
 * Creates a centralized alert store with proper typing
 */
function createAlertStore() {
	// State variables with proper types
	let showAlert = $state(false);
	let alertTitle = $state<string>("");
	let alertMessage = $state<string>("");
	let alertIsError = $state<boolean>(false);
	let alertIsAwaitError = $state<boolean>(false);
	let alertCallback = $state<AlertCallback | null>(null);

	return {
		// Getters for alert state
		get isAlertShown() {
			return showAlert;
		},
		get title() {
			return alertTitle;
		},
		get message() {
			return alertMessage;
		},
		get isError() {
			return alertIsError;
		},
		get isAwaitError() {
			return alertIsAwaitError;
		},
		get callback() {
			return alertCallback;
		},

		// Method to set alert state
		showAlert(
			title: string,
			message: string,
			isError: boolean | undefined = false,
			isAwaitError: boolean | undefined = false,
			onClick: AlertCallback | null = null,
		) {
			showAlert = true;
			alertTitle = title;
			alertMessage = message;
			alertIsError = isError;
			alertIsAwaitError = isAwaitError;
			alertCallback = onClick;
		},

		// Method to hide alert and reset state so that they do not reappear as stale alerts.
		hideAlert() {
			showAlert = false;
			alertTitle = "";
			alertMessage = "";
			alertIsError = false;
			alertIsAwaitError = false;
			alertCallback = null;
		},
	};
}

export const alertStoreSvelte = createAlertStore();
