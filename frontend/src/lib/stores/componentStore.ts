import AdminPage from "$lib/components/AdminPage.svelte";
import ChildrenGallery from "$lib/components/ChildrenGallery.svelte";
import ChildrenRegistration from "$lib/components/ChildrenRegistration.svelte";
import DateInput from "$lib/components/DataInput/DateInput.svelte";
import Fileupload from "$lib/components/DataInput/Fileupload.svelte";
import RadioList from "$lib/components/DataInput/RadioList.svelte";
import Milestone from "$lib/components/Milestone.svelte";
import MilestoneGroup from "$lib/components/MilestoneGroup.svelte";
import MilestoneOverview from "$lib/components/MilestoneOverview.svelte";
import UserDataInput from "$lib/components/UserDataInput.svelte";
import { Card, Input, MultiSelect, Select, Textarea } from "flowbite-svelte";
import { writable } from "svelte/store";

interface ComponentTable {
	[key: string]: any; // README: flowbite components are not yet svelte5 => 'Component' type which should be used instead of 'any' here throws errors for flowbite components.
}

export const componentTable: ComponentTable = {
	userDataInput: UserDataInput,
	childrenGallery: ChildrenGallery,
	childrenRegistration: ChildrenRegistration,
	milestoneGroup: MilestoneGroup,
	milestoneOverview: MilestoneOverview,
	milestone: Milestone,
	radioList: RadioList,
	input: Input,
	date: DateInput,
	multiSelect: MultiSelect,
	select: Select,
	fileupload: Fileupload,
	textarea: Textarea,
	adminPage: AdminPage,
	researchPage: Card,
};

// used in userlandingpage to make it single page
export const activeTabPersonal = writable("userDataInput");
export const activeTabChildren = writable("childrenGallery");
