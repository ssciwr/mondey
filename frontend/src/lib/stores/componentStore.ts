import AdminPage from "$lib/components/AdminPage.svelte";
import ChildrenOverview from "$lib/components/ChildrenOverview.svelte";
import ChildrenRegistration from "$lib/components/ChildrenRegistration.svelte";
import DateInput from "$lib/components/DataInput/DateInput.svelte";
import RadioList from "$lib/components/DataInput/RadioList.svelte";
import Milestone from "$lib/components/Milestone.svelte";
import MilestoneGroup from "$lib/components/MilestoneGroup.svelte";
import MilestoneOverview from "$lib/components/MilestoneOverview.svelte";
import UserDataInput from "$lib/components/UserDataInput.svelte";
import {
	Card,
	Fileupload,
	Input,
	MultiSelect,
	Select,
	Textarea,
} from "flowbite-svelte";
import type { Component } from "svelte";
import { writable } from "svelte/store";

interface ComponentTable {
	[key: string]: Component;
}

// put all the components here. can be an expanding list
export const componentTable: ComponentTable = {
	userDataInput: UserDataInput,
	childrenGallery: ChildrenOverview,
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
export const activeTabPersonal = writable("userDataInput");
export const activeTabChildren = writable("childrenGallery");
