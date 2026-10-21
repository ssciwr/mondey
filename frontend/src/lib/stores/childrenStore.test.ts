import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
	getChild: vi.fn(),
}));

vi.mock("#lib/client/index.ts", () => ({
	getChild: mocks.getChild,
}));

import { currentChild } from "#lib/stores/childrenStore.svelte.ts";

function child(id: number) {
	return { id, name: `child ${id}`, birth_month: 1, birth_year: 2024 };
}

describe("currentChild", () => {
	beforeEach(() => {
		mocks.getChild.mockReset();
		currentChild.id = null;
	});

	it("loads the data of the selected child", async () => {
		mocks.getChild.mockResolvedValue({ data: child(1) });
		currentChild.id = 1;
		await currentChild.load_data();
		expect(currentChild.name).toBe("child 1");
		expect(mocks.getChild).toHaveBeenCalledTimes(1);
	});

	it("does not request the same child twice while a request is in progress", async () => {
		const response = Promise.withResolvers();
		mocks.getChild.mockReturnValue(response.promise);
		currentChild.id = 1;
		const loaded = currentChild.load_data();
		response.resolve({ data: child(1) });
		await loaded;
		expect(mocks.getChild).toHaveBeenCalledTimes(1);
		expect(currentChild.name).toBe("child 1");
	});

	it("ignores the response for a child that is no longer selected", async () => {
		const first = Promise.withResolvers();
		const second = Promise.withResolvers();
		mocks.getChild
			.mockReturnValueOnce(first.promise)
			.mockReturnValueOnce(second.promise);
		currentChild.id = 1;
		currentChild.id = 2;
		const loaded = currentChild.load_data();
		second.resolve({ data: child(2) });
		await loaded;
		// the slower response for the first child arrives last
		first.resolve({ data: child(1) });
		await Promise.resolve();
		await Promise.resolve();
		expect(currentChild.id).toBe(2);
		expect(currentChild.name).toBe("child 2");
	});

	it("handles a failed request", async () => {
		const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
		mocks.getChild.mockRejectedValue(new TypeError("Failed to fetch"));
		currentChild.id = 1;
		await expect(currentChild.load_data()).resolves.toBeUndefined();
		expect(currentChild.data).toBeNull();
		expect(log).toHaveBeenCalled();
		log.mockRestore();
	});
});
