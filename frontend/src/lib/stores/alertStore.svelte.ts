type AlertCallback = () => void;

/**
 * Creates a centralized alert store with proper typing
 * What this will do is show an alert on the page when you call showAlert.
 *
 * However note that if you use it in a await-data-catch pattern like this:
 *
 * await promise...
 *  <Spinner>
 * then data...
 * <div>{data}</div>
 * catch error..
 * showAlert(error.message,...)
 *
 * --> Then it will show for errors related to the promise/await, but it won't show for errors during interactive page
 * use (by design). E.g. if you have something in the data - div bit which throws an Exception, by default, no alert
 * will show. You need to manually catch and invoke with specific (and translated) errors to use this.
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
		set isAlertShown(value: boolean) {
			showAlert = value;
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

export const alertStore = createAlertStore();
