import { isDark } from "$lib/components/DataDisplay/color_utils";
import { describe, expect, it } from "vitest";

describe("isDark", () => {
	for (const color of [
		null,
		"#ffffff",
		"#a2a9c0",
		"#b2b9c0",
		"#7898ff",
		"#ee9876",
	]) {
		it(`${color} is not dark`, () => {
			expect(isDark(color)).toBe(false);
		});
	}
	for (const color of [
		"#000000",
		"#427562",
		"#a76050",
		"#476613",
		"#990000",
		"#8500aa",
	]) {
		it(`${color} is dark`, () => {
			expect(isDark(color)).toBe(true);
		});
	}
});
