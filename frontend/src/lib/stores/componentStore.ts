import DateInput from "$lib/components/DataInput/DateInput.svelte";
import Fileupload from "$lib/components/DataInput/Fileupload.svelte";
import RadioList from "$lib/components/DataInput/RadioList.svelte";
import { Input, MultiSelect, Select, Textarea } from "flowbite-svelte";
import { writable } from "svelte/store";

interface ComponentTable {
	[key: string]: any; // README: flowbite components are not yet svelte5 => 'Component' type which should be used instead of 'any' here throws errors for flowbite components.
}

export const componentTable: ComponentTable = {
	radioList: RadioList,
	input: Input,
	date: DateInput,
	multiSelect: MultiSelect,
	select: Select,
	fileupload: Fileupload,
	textarea: Textarea,
};

// used in userlandingpage to make it single page
export const activePage = writable("userDataInput");
