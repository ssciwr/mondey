import { describe, expect, it } from "vitest";
import { serializeCsv } from "./csv";

describe("serializeCsv", () => {
	it("escapes headers and values using CSV quoting rules", () => {
		const csv = serializeCsv(
			[
				"child_age",
				"Hat das Kind in einem der nachfolgenden Entwicklungsbereiche Probleme, wegen denen es schon einmal in Behandlung /war?",
				'Say "hello"',
			],
			[
				[12, "Denken, Sprache", 'A "quoted" answer'],
				[13, "first line\nsecond line", null],
			],
		);

		expect(csv).toBe(
			'"child_age","Hat das Kind in einem der nachfolgenden Entwicklungsbereiche Probleme, wegen denen es schon einmal in Behandlung /war?","Say ""hello"""\n' +
				'"12","Denken, Sprache","A ""quoted"" answer"\n' +
				'"13","first line\nsecond line",\n',
		);
	});
});
