function escapeCsvField(value: unknown): string {
	if (value === null || value === undefined) {
		return "";
	}
	return `"${String(value).replaceAll('"', '""')}"`;
}

export function serializeCsv(columns: unknown[], rows: unknown[][]): string {
	const lines = [
		columns.map(escapeCsvField).join(","),
		...rows.map((row) => row.map(escapeCsvField).join(",")),
	];
	return `${lines.join("\n")}\n`;
}
