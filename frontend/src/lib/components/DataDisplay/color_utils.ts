import { contrastRatio } from "wcag-contrast-utils";

export function isDark(bgColor: string | null | undefined): boolean {
	if (!bgColor) {
		return false;
	}
	return contrastRatio("#ffffff", bgColor) > contrastRatio("#000000", bgColor);
}
