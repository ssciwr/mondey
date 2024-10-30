import {
	filterItems,
	makePlaceholderText,
} from "$lib/components/DataDisplay/TableDisplay.svelte";

import { describe, expect, it } from "vitest";

describe("filterItems: should return items in given columns ", () => {
	const data = [
		{ id: 1, name: "John", age: 25 },
		{ id: 2, name: "Jane", age: 30 },
		{ id: 3, name: "Bob", age: 28 },
	];
	const searchableColumns = ["name", "age"];

	it("should return all items when the search term is empty", () => {
		const searchTerm = "";
		const result = filterItems(data, searchTerm, searchableColumns);
		expect(result).toEqual(data);
	});

	it("should return no items when the search term has no overlap with entries of searchable columns", () => {
		const searchTerm = 1;
		const result = filterItems(data, searchTerm, searchableColumns);
		expect(result).toEqual([]);
	});

	it("should return items case sensitively", () => {
		const searchTermUpper = "Bob";
		const searchTermLower = "bob";
		const resultUpper = filterItems(data, searchTermUpper, searchableColumns);
		const resultLower = filterItems(data, searchTermLower, searchableColumns);
		expect(resultLower).toEqual([]);
		expect(resultUpper).toEqual([{ id: 3, name: "Bob", age: 28 }]);
	});

	it("should return nothing if there are no searchable columns", () => {
		const otherSearchableColumns = [];
		const searchTerm = "Jane";
		const result = filterItems(data, searchTerm, otherSearchableColumns);
		expect(result).toEqual([]);
	});
});

describe("makePlaceholderText: should return a placeholder text based on the number of searchable columns", () => {
	const data = [
		{ id: 1, name: "John", age: 25, income: 30000 },
		{ id: 2, name: "Jane", age: 30, income: 35000 },
		{ id: 3, name: "Bob", age: 28, income: 33000 },
	];

	it("should return colname when only one searchable columns", () => {
		const searchableColumns = ["name"];
		const result = makePlaceholderText(data, searchableColumns);
		expect(result).toEqual("Filter name");
	});
	it("should return with except when searchable colnames are more than half of the colnames", () => {
		const searchableColumns = ["name", "age", "income"];
		const result = makePlaceholderText(data, searchableColumns);
		expect(result).toEqual("Filter all columns except id");
	});
	it("should return with list when searchable colnames are less than half of the colnames", () => {
		const searchableColumns = ["name", "age"];
		const result = makePlaceholderText(data, searchableColumns);
		expect(result).toEqual("Filter any of name, age");
	});
	it("should return with all when searchable colnames are less than half of the colnames", () => {
		const searchableColumns = ["name", "age", "income", "id"];
		const result = makePlaceholderText(data, searchableColumns);
		expect(result).toEqual("Filter all columns");
	});

	it("should return with all when searchable colnames are less than half of the colnames", () => {
		const searchableColumns = [];
		const result = makePlaceholderText(data, searchableColumns);
		expect(result).toEqual("Filter disabled");
	});
});
