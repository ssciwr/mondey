import { ReadableStream } from "node:stream/web";
import { TextDecoder, TextEncoder } from "node:util";
import { describe, expect, it, vi } from "vitest";
import { readResearchStream } from "./progress";

vi.stubGlobal("TextDecoder", TextDecoder);

const encoder = new TextEncoder();
const progress = { type: "progress", stage: "milestoneAnswers" };

function stream(text: string, chunkSize = 1) {
	const bytes = encoder.encode(text);
	return new ReadableStream<Uint8Array>({
		start(controller) {
			for (let i = 0; i < bytes.length; i += chunkSize) {
				controller.enqueue(bytes.slice(i, i + chunkSize));
			}
			controller.close();
		},
	}) as globalThis.ReadableStream<Uint8Array>;
}

describe("research progress stream", () => {
	it("handles fragmented records and UTF-8, and multiple records in one chunk", async () => {
		for (const chunkSize of [1, 7, 10000]) {
			const onProgress = vi.fn();
			const data = [{ child_question_1: "Größe 🐣" }];
			const body = `${JSON.stringify(progress)}\n${JSON.stringify({ type: "data", data })}\n`;
			expect(
				await readResearchStream(stream(body, chunkSize), onProgress),
			).toEqual(data);
			expect(onProgress).toHaveBeenCalledWith("milestoneAnswers");
		}
	});

	it("reports progress while still waiting for the result", async () => {
		let controller!: ReadableStreamDefaultController<Uint8Array>;
		const source = new ReadableStream<Uint8Array>({
			start(value) {
				controller = value;
			},
		});
		const onProgress = vi.fn();
		const result = readResearchStream(
			source as globalThis.ReadableStream<Uint8Array>,
			onProgress,
		);
		controller.enqueue(encoder.encode(`${JSON.stringify(progress)}\n`));
		await vi.waitFor(() =>
			expect(onProgress).toHaveBeenCalledWith("milestoneAnswers"),
		);
		controller.enqueue(encoder.encode('{"type":"data","data":[]}\n'));
		controller.close();
		expect(await result).toEqual([]);
	});

	it("skips stages it does not know", async () => {
		const onProgress = vi.fn();
		const body = `${JSON.stringify({ type: "progress", stage: "newStage" })}\n${JSON.stringify(progress)}\n{"type":"data","data":[]}\n`;
		expect(await readResearchStream(stream(body), onProgress)).toEqual([]);
		expect(onProgress.mock.calls).toEqual([["milestoneAnswers"]]);
	});

	it.each([
		'{"type":"error"}\n',
		'{"type":"invalid"}\n',
		'{"type":"data","data":[',
		`${JSON.stringify(progress)}\n`,
		"not json\n",
	])(
		"rejects errors, invalid events, and truncated responses: %s",
		async (body) => {
			await expect(readResearchStream(stream(body), vi.fn())).rejects.toThrow();
		},
	);
});
