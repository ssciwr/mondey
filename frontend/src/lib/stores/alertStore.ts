type AlertCallback = () => void;

/**
 * Creates a centralized alert store with proper typing
 */
function createAlertStore() {
    // State variables with proper types
    let showAlert = $state(false);
    let alertMessage = $state<string | null>(null);
    let alertError = $state<string | null>(null);
    let alertCallback = $state<AlertCallback | null>(null);

    return {
        // Getters for alert state
        get isAlertShown() {
            return showAlert;
        },
        get message() {
            return alertMessage;
        },
        get error() {
            return alertError;
        },
        get callback() {
            return alertCallback;
        },

        // Method to set alert state
        showAlert(message: string, error: string | null = null, onClick: AlertCallback | null = null) {
            showAlert = true;
            alertMessage = message;
            alertError = error;
            alertCallback = onClick;
        },

        // Method to hide alert and reset state
        hideAlert() {
            showAlert = false;
            alertMessage = null;
            alertError = null;
            alertCallback = null;
        }
    };
}

export const alertStore = createAlertStore();
