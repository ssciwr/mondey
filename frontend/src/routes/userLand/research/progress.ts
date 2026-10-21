import { type ResearchStage, researchStages } from "./utilTypes";

// A record may span network chunks, including within a UTF-8 character.
// Keep fragments until the newline to avoid repeatedly copying a large dataset.
export async function readResearchStream(
	stream: ReadableStream<Uint8Array>,
	onProgress: (stage: ResearchStage) => void,
): Promise<Record<string, unknown>[]> {
	const reader = stream.getReader();
	const decoder = new TextDecoder();
	let fragments: string[] = [];
	try {
		while (true) {
			const { value, done } = await reader.read();
			const text = decoder.decode(value, { stream: !done });
			let start = 0;
			for (
				let end = text.indexOf("\n");
				end !== -1;
				end = text.indexOf("\n", start)
			) {
				fragments.push(text.slice(start, end));
				const line = fragments.join("");
				fragments = [];
				start = end + 1;
				if (!line.trim()) continue;
				const event = JSON.parse(line);
				if (event.type === "error")
					throw new Error("Research extraction failed");
				if (event.type === "data" && Array.isArray(event.data))
					return event.data;
				if (event.type !== "progress")
					throw new Error("Invalid research stream event");
				// Stages unknown to this client, e.g. added to the backend later, are skipped.
				if (researchStages.includes(event.stage)) onProgress(event.stage);
			}
			if (start < text.length) fragments.push(text.slice(start));
			if (done)
				throw new Error("Research stream ended before the data arrived");
		}
	} finally {
		await reader.cancel().catch(() => {
			// A broken connection may already have closed the stream.
		});
	}
}
