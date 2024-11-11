import { writable } from "svelte/store";

export const currentChild = writable(null as null | number);
