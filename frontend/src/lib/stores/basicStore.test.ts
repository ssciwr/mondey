import { BasicStore } from "$lib/stores/basicStore";
import { describe, expect, it } from "vitest";

describe("normal functionality", () => {
	const dummyData = {
		name: "A",
		id: "idA",
		role: "user",
	};
	const dummyUsers = {
		dummyA: dummyData,
		dummyB: dummyData,
		dummyC: dummyData,
	};

	const users = new BasicStore("users", "dummy");
	users.set(dummyUsers);

	it("construction", async () => {
		const otheruser = new BasicStore("otheruser", "otherdummy");
		otheruser.set(dummyUsers);
		expect(users.get()).toEqual(dummyUsers);
	});

	it("data", async () => {
		const userstore = new BasicStore("user", "thing");
		userstore.set(dummyUsers);

		expect(userstore.get()).toEqual(dummyUsers);
	});

	it("successful user addition", async () => {
		users.set(dummyUsers);
		users.add("anotherUser", { name: "B", role: "admin", id: "idB" });
		expect(users.get()["anotherUser"]).toEqual({
			name: "B",
			role: "admin",
			id: "idB",
		});
	});

	it("sucessful user removal", async () => {
		users.set(dummyUsers);
		users.remove("dummyA");
		expect(users.get()["dummyA"]).toEqual(undefined);
	});

	it("succesful user update", async () => {
		users.set(dummyUsers);
		users.update("dummyB", { name: "B", id: "thing", role: "admin" });
		expect(users.get()["dummyB"]).toEqual({
			name: "B",
			id: "thing",
			role: "admin",
		});
	});
});
